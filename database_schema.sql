--
-- PostgreSQL database dump
--

\restrict yDqInBog2ki06exhQvg4DAVJIVn6acbu4zapT7BNMBfiVdtsGudatVYLSvXoT00

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: get_student_course_count(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.get_student_course_count(p_student_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    course_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO course_count
    FROM enrollments
    WHERE student_id = p_student_id
      AND status = 'active';

    RETURN course_count;
END;
$$;


--
-- Name: update_lecture_timestamp(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_lecture_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.uploaded_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.courses (
    course_id bigint NOT NULL,
    course_code character varying(20) NOT NULL,
    course_name character varying(150) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    instructor_id bigint
);


--
-- Name: courses_course_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.courses ALTER COLUMN course_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.courses_course_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: enrollments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enrollments (
    enrollment_id bigint NOT NULL,
    student_id bigint NOT NULL,
    course_id bigint NOT NULL,
    enrolled_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    CONSTRAINT enrollments_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'completed'::character varying, 'dropped'::character varying])::text[])))
);


--
-- Name: enrollments_enrollment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.enrollments ALTER COLUMN enrollment_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.enrollments_enrollment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: lecture_chunks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lecture_chunks (
    chunk_id bigint NOT NULL,
    lecture_id bigint NOT NULL,
    chunk_text text NOT NULL,
    chunk_index integer NOT NULL
);


--
-- Name: lecture_chunks_chunk_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.lecture_chunks ALTER COLUMN chunk_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.lecture_chunks_chunk_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: lecture_embeddings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lecture_embeddings (
    chunk_id bigint NOT NULL,
    embedding public.vector(384) NOT NULL
);


--
-- Name: lectures; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lectures (
    lecture_id bigint NOT NULL,
    course_id bigint NOT NULL,
    title character varying(255) NOT NULL,
    file_path text NOT NULL,
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: lectures_lecture_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.lectures ALTER COLUMN lecture_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.lectures_lecture_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id bigint NOT NULL,
    full_name character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    password_hash text NOT NULL,
    role character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['student'::character varying, 'instructor'::character varying])::text[])))
);


--
-- Name: student_course_details; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.student_course_details AS
 SELECT u.user_id,
    u.full_name AS student_name,
    u.email,
    c.course_id,
    c.course_code,
    c.course_name,
    e.enrolled_at,
    e.status AS enrollment_status
   FROM ((public.users u
     JOIN public.enrollments e ON ((u.user_id = e.student_id)))
     JOIN public.courses c ON ((e.course_id = c.course_id)));


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users ALTER COLUMN user_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: courses courses_course_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_course_code_key UNIQUE (course_code);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (course_id);


--
-- Name: enrollments enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_pkey PRIMARY KEY (enrollment_id);


--
-- Name: enrollments enrollments_student_id_course_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_student_id_course_id_key UNIQUE (student_id, course_id);


--
-- Name: lecture_chunks lecture_chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecture_chunks
    ADD CONSTRAINT lecture_chunks_pkey PRIMARY KEY (chunk_id);


--
-- Name: lecture_embeddings lecture_embeddings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecture_embeddings
    ADD CONSTRAINT lecture_embeddings_pkey PRIMARY KEY (chunk_id);


--
-- Name: lectures lectures_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lectures
    ADD CONSTRAINT lectures_pkey PRIMARY KEY (lecture_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: idx_courses_instructor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_courses_instructor ON public.courses USING btree (instructor_id);


--
-- Name: idx_enrollments_course; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_enrollments_course ON public.enrollments USING btree (course_id);


--
-- Name: idx_enrollments_student; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_enrollments_student ON public.enrollments USING btree (student_id);


--
-- Name: idx_lectures_course; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_lectures_course ON public.lectures USING btree (course_id);


--
-- Name: lecture_embeddings_hnsw_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX lecture_embeddings_hnsw_idx ON public.lecture_embeddings USING hnsw (embedding public.vector_cosine_ops);


--
-- Name: lectures lecture_timestamp_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER lecture_timestamp_trigger BEFORE UPDATE ON public.lectures FOR EACH ROW EXECUTE FUNCTION public.update_lecture_timestamp();


--
-- Name: enrollments enrollments_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON DELETE CASCADE;


--
-- Name: enrollments enrollments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: courses fk_courses_instructor; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT fk_courses_instructor FOREIGN KEY (instructor_id) REFERENCES public.users(user_id) ON DELETE SET NULL;


--
-- Name: lectures fk_lectures_course; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lectures
    ADD CONSTRAINT fk_lectures_course FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON DELETE CASCADE;


--
-- Name: lecture_chunks lecture_chunks_lecture_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecture_chunks
    ADD CONSTRAINT lecture_chunks_lecture_id_fkey FOREIGN KEY (lecture_id) REFERENCES public.lectures(lecture_id) ON DELETE CASCADE;


--
-- Name: lecture_embeddings lecture_embeddings_chunk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lecture_embeddings
    ADD CONSTRAINT lecture_embeddings_chunk_id_fkey FOREIGN KEY (chunk_id) REFERENCES public.lecture_chunks(chunk_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict yDqInBog2ki06exhQvg4DAVJIVn6acbu4zapT7BNMBfiVdtsGudatVYLSvXoT00

