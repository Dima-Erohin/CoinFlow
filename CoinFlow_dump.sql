--
-- PostgreSQL database dump
--

\restrict aBXOYot7uUhnNOmKuBXVvXuuTuGxQbEld1zQpsP4a6sTOPSdnF6dGcM9CBELr2j

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2025-09-21 11:53:19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 219 (class 1255 OID 16400)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 217 (class 1259 OID 16389)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    sub_ids bigint[] DEFAULT '{}'::bigint[],
    email text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16403)
-- Name: users_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.users_view AS
 SELECT id,
    sub_ids,
    email
   FROM public.users;


ALTER VIEW public.users_view OWNER TO postgres;

--
-- TOC entry 4798 (class 0 OID 16389)
-- Dependencies: 217
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, sub_ids, email, created_at, updated_at) FROM stdin;
987654321	{123456789,333444555}	user2@example.com	2025-09-21 11:31:44.36785	2025-09-21 11:31:44.376689
555666777	{111222333}	user3@example.com	2025-09-21 11:31:44.369517	2025-09-21 11:31:44.378793
123456789	{987654321,444555666,777888999}	newemail1@example.com	2025-09-21 11:31:44.364096	2025-09-21 11:31:44.381217
\.


--
-- TOC entry 4650 (class 2606 OID 16398)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4648 (class 1259 OID 16399)
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email ON public.users USING btree (email) WHERE (email IS NOT NULL);


--
-- TOC entry 4651 (class 2620 OID 16402)
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


-- Completed on 2025-09-21 11:53:19

--
-- PostgreSQL database dump complete
--

\unrestrict aBXOYot7uUhnNOmKuBXVvXuuTuGxQbEld1zQpsP4a6sTOPSdnF6dGcM9CBELr2j

