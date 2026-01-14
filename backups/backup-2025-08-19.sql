--
-- PostgreSQL database dump
--

\restrict EIv9Fz9RpqUJewi36ceR42EDeZ7q53a9jDJocKAmg6FNOF7owcEbrcT3W0wc9Gd

-- Dumped from database version 16.9 (Debian 16.9-1.pgdg120+1)
-- Dumped by pg_dump version 17.6

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
-- Name: public; Type: SCHEMA; Schema: -; Owner: folgas_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO folgas_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agendamento; Type: TABLE; Schema: public; Owner: folgas_user
--

CREATE TABLE public.agendamento (
    id integer NOT NULL,
    funcionario_id integer NOT NULL,
    status character varying(50) NOT NULL,
    data date NOT NULL,
    motivo character varying(100) NOT NULL,
    tipo_folga character varying(50),
    data_referencia date,
    horas integer,
    minutos integer,
    substituicao character varying(3) DEFAULT 'Não'::character varying NOT NULL,
    nome_substituto character varying(255),
    conferido boolean DEFAULT false
);


ALTER TABLE public.agendamento OWNER TO folgas_user;

--
-- Name: agendamento_id_seq; Type: SEQUENCE; Schema: public; Owner: folgas_user
--

CREATE SEQUENCE public.agendamento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agendamento_id_seq OWNER TO folgas_user;

--
-- Name: agendamento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: folgas_user
--

ALTER SEQUENCE public.agendamento_id_seq OWNED BY public.agendamento.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: folgas_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO folgas_user;

--
-- Name: banco_de_horas; Type: TABLE; Schema: public; Owner: folgas_user
--

CREATE TABLE public.banco_de_horas (
    id integer NOT NULL,
    funcionario_id integer NOT NULL,
    horas integer NOT NULL,
    minutos integer NOT NULL,
    total_minutos integer,
    data_realizacao date NOT NULL,
    status character varying(50),
    data_criacao timestamp without time zone,
    data_atualizacao timestamp without time zone,
    motivo character varying(40),
    usufruido boolean
);


ALTER TABLE public.banco_de_horas OWNER TO folgas_user;

--
-- Name: banco_de_horas_id_seq; Type: SEQUENCE; Schema: public; Owner: folgas_user
--

CREATE SEQUENCE public.banco_de_horas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.banco_de_horas_id_seq OWNER TO folgas_user;

--
-- Name: banco_de_horas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: folgas_user
--

ALTER SEQUENCE public.banco_de_horas_id_seq OWNED BY public.banco_de_horas.id;


--
-- Name: esquecimento_ponto; Type: TABLE; Schema: public; Owner: folgas_user
--

CREATE TABLE public.esquecimento_ponto (
    id integer NOT NULL,
    nome character varying(150) NOT NULL,
    registro character varying(150) NOT NULL,
    data_esquecimento date NOT NULL,
    hora_primeira_entrada character varying(5),
    hora_primeira_saida character varying(5),
    hora_segunda_entrada character varying(5),
    hora_segunda_saida character varying(5),
    user_id integer NOT NULL,
    conferido boolean DEFAULT false,
    motivo text
);


ALTER TABLE public.esquecimento_ponto OWNER TO folgas_user;

--
-- Name: esquecimento_ponto_id_seq; Type: SEQUENCE; Schema: public; Owner: folgas_user
--

CREATE SEQUENCE public.esquecimento_ponto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.esquecimento_ponto_id_seq OWNER TO folgas_user;

--
-- Name: esquecimento_ponto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: folgas_user
--

ALTER SEQUENCE public.esquecimento_ponto_id_seq OWNED BY public.esquecimento_ponto.id;


--
-- Name: folga; Type: TABLE; Schema: public; Owner: folgas_user
--

CREATE TABLE public.folga (
    id integer NOT NULL,
    funcionario_id integer NOT NULL,
    data date NOT NULL,
    motivo character varying(50) NOT NULL,
    status character varying(50)
);


ALTER TABLE public.folga OWNER TO folgas_user;

--
-- Name: folga_id_seq; Type: SEQUENCE; Schema: public; Owner: folgas_user
--

CREATE SEQUENCE public.folga_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.folga_id_seq OWNER TO folgas_user;

--
-- Name: folga_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: folgas_user
--

ALTER SEQUENCE public.folga_id_seq OWNED BY public.folga.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: folgas_user
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    nome character varying(150) NOT NULL,
    registro character varying(150) NOT NULL,
    email character varying(150) NOT NULL,
    senha character varying(256) NOT NULL,
    tipo character varying(20) NOT NULL,
    banco_horas integer NOT NULL,
    status character varying(20),
    celular character varying(20),
    data_nascimento date,
    tre_total integer DEFAULT 0 NOT NULL,
    tre_usufruidas integer DEFAULT 0 NOT NULL,
    cpf character varying(14),
    rg character varying(20),
    data_emissao_rg date,
    orgao_emissor character varying(50),
    graduacao character varying(50),
    cargo character varying(100),
    aceitou_termo boolean DEFAULT false,
    versao_termo character varying(20),
    CONSTRAINT user_graduacao_check CHECK (((graduacao)::text = ANY ((ARRAY['Técnico'::character varying, 'Tecnólogo'::character varying, 'Licenciatura'::character varying, 'Pós Graduação Latu Sensu'::character varying, 'Mestrado'::character varying, 'Doutorado'::character varying, 'Pós Doutorado'::character varying])::text[])))
);


ALTER TABLE public."user" OWNER TO folgas_user;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: folgas_user
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO folgas_user;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: folgas_user
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: agendamento id; Type: DEFAULT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.agendamento ALTER COLUMN id SET DEFAULT nextval('public.agendamento_id_seq'::regclass);


--
-- Name: banco_de_horas id; Type: DEFAULT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.banco_de_horas ALTER COLUMN id SET DEFAULT nextval('public.banco_de_horas_id_seq'::regclass);


--
-- Name: esquecimento_ponto id; Type: DEFAULT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.esquecimento_ponto ALTER COLUMN id SET DEFAULT nextval('public.esquecimento_ponto_id_seq'::regclass);


--
-- Name: folga id; Type: DEFAULT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.folga ALTER COLUMN id SET DEFAULT nextval('public.folga_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: agendamento; Type: TABLE DATA; Schema: public; Owner: folgas_user
--

COPY public.agendamento (id, funcionario_id, status, data, motivo, tipo_folga, data_referencia, horas, minutos, substituicao, nome_substituto, conferido) FROM stdin;
2	3	deferido	2025-02-03	TRE	TRE	\N	0	0	Não	\N	t
37	12	deferido	2025-02-03	BH	BH	2025-02-03	1	20	Não	\N	t
76	37	deferido	2025-02-28	AB		\N	0	0	Não	\N	t
73	48	deferido	2025-02-11	AB		\N	0	0	Não	\N	t
159	65	deferido	2025-03-07	BH	BH	2025-02-22	0	0	Não	\N	t
95	50	deferido	2025-02-24	AB		\N	0	0	Não	\N	t
35	14	deferido	2025-02-14	AB		\N	0	0	Não	\N	t
45	35	deferido	2025-02-07	AB		\N	0	0	Não	\N	t
1	2	deferido	2025-02-03	TRE	TRE	\N	0	0	Não	\N	t
99	2	deferido	2025-02-26	AB		\N	0	0	Não	\N	t
94	19	deferido	2025-02-20	TRE	TRE	\N	0	0	Não	\N	t
305	71	deferido	2025-06-12	AB		\N	0	0	Não	\N	f
71	3	deferido	2025-02-17	AB		\N	0	0	Não	\N	t
58	30	deferido	2025-03-07	BH	BH	2024-09-28	8	0	Não	\N	t
97	32	deferido	2025-03-10	AB		\N	0	0	Não	\N	t
72	41	deferido	2025-02-21	AB		\N	0	0	Não	\N	t
79	51	deferido	2025-03-10	AB		\N	0	0	Não	\N	t
308	16	deferido	2025-06-16	AB		\N	0	0	Não	\N	f
116	62	deferido	2025-03-06	AB		\N	0	0	Não	\N	t
115	49	deferido	2025-03-07	TRE	TRE	\N	0	0	Não	\N	t
152	2	deferido	2025-03-14	AB		\N	0	0	Não	\N	t
105	56	deferido	2025-02-27	AB		\N	0	0	Não	\N	t
40	21	deferido	2025-03-06	AB	AB	\N	0	0	Não	\N	t
151	44	deferido	2025-03-10	AB		\N	0	0	Não	\N	t
112	61	deferido	2025-03-10	AB		\N	0	0	Não	\N	t
102	35	deferido	2025-03-06	AB		\N	0	0	Não	\N	t
104	37	deferido	2025-03-07	AB		\N	0	0	Não	\N	t
42	30	deferido	2025-03-06	AB		\N	0	0	Não	\N	t
48	33	deferido	2025-02-28	AB		\N	0	0	Não	\N	t
75	46	deferido	2025-02-14	AB		\N	0	0	Não	\N	t
39	21	deferido	2025-02-28	TRE	TRE	\N	0	0	Não	\N	t
46	37	deferido	2025-02-07	BH	BH	2025-02-04	2	8	Não	\N	t
155	57	deferido	2025-03-10	AB		\N	0	0	Não	\N	t
52	38	deferido	2025-03-14	AB		\N	0	0	Não	\N	t
167	28	deferido	2025-03-14	AB		\N	0	0	Não	\N	t
154	59	deferido	2025-03-17	AB		\N	0	0	Não	\N	t
166	28	deferido	2025-03-17	TRE	TRE	\N	0	0	Não	\N	t
32	18	deferido	2025-02-10	AB		\N	0	0	Não	\N	t
153	2	deferido	2025-03-17	TRE	TRE	\N	0	0	Não	\N	t
149	63	deferido	2025-03-21	AB		\N	0	0	Não	\N	t
96	54	deferido	2025-03-21	AB		\N	0	0	Não	\N	t
103	35	deferido	2025-04-04	AB		\N	0	0	Não	\N	t
107	29	deferido	2025-03-07	AB		\N	0	0	Não	\N	t
98	51	deferido	2025-02-24	AB	AB	\N	0	0	Não	\N	t
156	46	deferido	2025-03-24	AB		\N	0	0	Não	\N	t
31	16	deferido	2025-02-24	AB		\N	0	0	Não	\N	t
47	31	deferido	2025-02-28	AB		\N	0	0	Não	\N	t
43	34	deferido	2025-02-14	AB		\N	0	0	Não	\N	t
100	19	deferido	2025-03-06	AB		\N	0	0	Não	\N	t
34	12	deferido	2025-02-14	AB		\N	0	0	Não	\N	t
106	57	deferido	2025-02-28	AB		\N	0	0	Não	\N	t
70	43	deferido	2025-02-28	AB		\N	0	0	Não	\N	t
160	37	deferido	2025-03-06	DS	DS	\N	0	0	Não	\N	t
101	19	deferido	2025-03-07	TRE	TRE	\N	0	0	Não	\N	t
164	23	deferido	2025-03-24	TRE	TRE	\N	0	0	Sim	Vanessa Primo ( já entrei em contato e combinei a substituição) 	t
168	55	deferido	2025-04-09	AB		\N	0	0	Não	\N	t
117	29	deferido	2025-04-16	AB		\N	0	0	Não	\N	t
113	32	deferido	2025-04-30	AB		\N	0	0	Não	\N	t
111	41	deferido	2025-04-28	AB		\N	0	0	Não	\N	t
157	66	deferido	2025-05-09	AB		\N	0	0	Não	\N	t
313	93	deferido	2025-05-30	AB		\N	0	0	Não	\N	f
109	59	deferido	2025-02-25	AB		\N	0	0	Não	\N	t
55	40	deferido	2025-02-28	AB		\N	0	0	Não	\N	t
158	65	deferido	2025-03-06	BH	BH	2025-02-22	0	0	Não	\N	t
309	74	deferido	2025-06-02	AB		\N	0	0	Não	\N	f
319	47	deferido	2025-06-06	AB		\N	0	0	Não	\N	f
150	63	deferido	2025-03-06	TRE	TRE	\N	0	0	Não	\N	t
110	60	deferido	2025-03-07	AB		\N	0	0	Não	\N	t
92	52	deferido	2025-02-25	AB		\N	0	0	Não	\N	t
161	35	deferido	2025-03-07	DS	DS	\N	0	0	Não	\N	t
74	47	deferido	2025-02-14	AB		\N	0	0	Não	\N	t
17	1	deferido	2025-03-06	AB		\N	0	0	Não	\N	t
51	39	deferido	2025-02-28	AB		\N	0	0	Não	\N	t
44	36	deferido	2025-02-07	AB		\N	0	0	Não	\N	t
78	49	deferido	2025-02-21	AB		\N	0	0	Não	\N	t
36	15	deferido	2025-02-17	AB		\N	0	0	Não	\N	t
315	23	deferido	2025-05-30	AB		\N	0	0	Não	\N	f
311	2	deferido	2025-06-02	AB		\N	0	0	Não	\N	f
91	36	deferido	2025-02-21	TRE	TRE	\N	0	0	Não	\N	t
93	25	deferido	2025-02-28	AB		\N	0	0	Não	\N	t
38	21	deferido	2025-02-27	AB		\N	0	0	Não	\N	t
33	18	deferido	2025-02-17	BH	BH	2025-02-05	8	0	Não	\N	t
108	58	deferido	2025-02-27	TRE	TRE	\N	0	0	Não	\N	t
49	33	deferido	2025-03-06	AB		\N	0	0	Não	\N	t
41	29	deferido	2025-02-10	AB		\N	0	0	Não	\N	t
147	63	deferido	2025-03-07	TRE	TRE	\N	0	0	Não	\N	t
77	19	deferido	2025-02-17	AB		\N	0	0	Não	\N	t
114	49	deferido	2025-03-06	TRE	TRE	\N	0	0	Não	\N	t
231	48	deferido	2025-04-11	AB		\N	0	0	Não	\N	t
243	52	deferido	2025-04-24	AB		\N	0	0	Não	\N	t
254	23	deferido	2025-04-16	DS	DS	\N	0	0	Não	\N	t
238	1	deferido	2025-04-14	AB		\N	0	0	Não	\N	t
218	77	deferido	2025-05-26	AB		\N	0	0	Não	\N	f
266	65	deferido	2025-05-05	AB		\N	0	0	Não	\N	t
213	69	deferido	2025-05-07	AB		\N	0	0	Não	\N	t
237	31	deferido	2025-05-07	AB		\N	0	0	Não	\N	t
257	47	deferido	2025-04-25	AB		\N	0	0	Não	\N	t
221	28	deferido	2025-04-25	TRE	TRE	\N	0	0	Não	\N	t
250	47	deferido	2025-05-27	TRE	TRE	\N	0	0	Não	\N	f
172	52	deferido	2025-03-11	DS	DS	\N	0	0	Não	\N	t
169	67	deferido	2025-03-13	AB		\N	0	0	Não	\N	t
178	70	deferido	2025-03-18	AB		\N	0	0	Não	\N	t
173	72	deferido	2025-03-19	AB		\N	0	0	Sim	Fabiana	t
196	66	deferido	2025-04-09	AB		\N	0	0	Não	\N	t
175	68	deferido	2025-03-19	AB		\N	0	0	Não	\N	t
174	51	deferido	2025-03-19	BH	BH	2024-08-15	8	0	Não	\N	t
205	76	deferido	2025-04-10	AB		\N	0	0	Não	\N	t
177	66	deferido	2025-03-20	AB		\N	0	0	Não	\N	t
163	23	deferido	2025-03-21	AB		\N	0	0	Sim	Vanessa Primo ( já entrei em contato e combinei a substituição) 	t
180	48	deferido	2025-03-21	AB		\N	0	0	Não	\N	t
182	45	deferido	2025-03-21	AB		\N	0	0	Não	\N	t
188	19	deferido	2025-04-02	AB		\N	0	0	Não	\N	f
189	75	deferido	2025-04-14	AB		\N	0	0	Não	\N	t
201	43	deferido	2025-04-14	TRE	TRE	\N	0	0	Não	\N	t
187	26	deferido	2025-03-24	TRE	TRE	\N	0	0	Não	\N	t
183	22	deferido	2025-03-25	AB		\N	0	0	Sim	Verificar	t
176	29	deferido	2025-03-28	BH	BH	2025-03-13	8	0	Não	\N	t
208	79	deferido	2025-04-22	AB		\N	0	0	Não	\N	t
236	83	deferido	2025-07-31	AB		\N	0	0	Não	\N	f
251	47	deferido	2025-05-28	TRE	TRE	\N	0	0	Não	\N	f
256	50	deferido	2025-10-24	AB		\N	0	0	Não	\N	f
207	79	deferido	2025-04-16	TRE	TRE	\N	0	0	Não	\N	t
272	2	deferido	2025-05-12	AB		\N	0	0	Não	\N	f
245	15	deferido	2025-05-16	AB		\N	0	0	Não	\N	f
209	59	deferido	2025-04-14	AB		\N	0	0	Não	\N	t
217	14	deferido	2025-04-11	AB		\N	0	0	Não	\N	t
219	12	deferido	2025-04-10	AB		\N	0	0	Não	\N	t
230	30	deferido	2025-05-19	AB		\N	0	0	Não	\N	f
239	69	deferido	2025-04-16	AB		\N	0	0	Não	\N	t
199	69	deferido	2025-03-21	DS	DS	\N	0	0	Não	\N	t
170	71	deferido	2025-03-28	AB		\N	0	0	Não	\N	t
185	74	deferido	2025-03-28	AB		\N	0	0	Não	\N	t
184	73	deferido	2025-03-28	AB		\N	0	0	Não	\N	t
179	55	deferido	2025-03-28	AB		\N	0	0	Não	\N	t
186	52	deferido	2025-03-31	AB		\N	0	0	Não	\N	t
210	51	deferido	2025-03-31	BH	BH	2024-10-15	8	0	Não	\N	t
195	20	deferido	2025-03-31	AB		\N	0	0	Não	\N	t
246	47	deferido	2025-05-21	AB		\N	0	0	Não	\N	f
197	65	deferido	2025-04-02	AB		\N	0	0	Não	\N	t
192	36	deferido	2025-04-03	AB		\N	0	0	Não	\N	t
198	82	deferido	2025-04-04	AB		\N	0	0	Não	\N	t
194	78	deferido	2025-04-07	AB		\N	0	0	Não	\N	t
203	73	deferido	2025-04-11	AB		\N	0	0	Não	\N	t
190	39	deferido	2025-04-07	AB		\N	0	0	Não	\N	t
247	47	deferido	2025-05-22	TRE	TRE	\N	0	0	Não	\N	f
204	64	deferido	2025-04-08	AB		\N	0	0	Não	\N	t
200	21	deferido	2025-04-08	AB		\N	0	0	Não	\N	t
202	62	deferido	2025-04-08	AB		\N	0	0	Não	\N	t
206	22	deferido	2025-04-08	AB		\N	0	0	Sim	Débora 	t
248	47	deferido	2025-05-23	TRE	TRE	\N	0	0	Não	\N	f
249	47	deferido	2025-05-26	TRE	TRE	\N	0	0	Não	\N	f
235	83	deferido	2025-08-01	AB		\N	0	0	Não	\N	f
171	37	deferido	2025-04-16	AB		\N	0	0	Não	\N	t
193	25	deferido	2025-04-16	AB		\N	0	0	Não	\N	t
264	54	deferido	2025-05-08	AB		\N	0	0	Não	\N	t
211	69	deferido	2025-05-05	TRE	TRE	\N	0	0	Não	\N	t
214	69	deferido	2025-07-31	AB		\N	0	0	Não	\N	f
215	69	deferido	2025-08-01	AB		\N	0	0	Não	\N	f
212	69	deferido	2025-05-06	TRE	TRE	\N	0	0	Não	\N	t
222	71	deferido	2025-04-25	AB		\N	0	0	Não	\N	t
241	77	deferido	2025-04-16	AB		\N	0	0	Não	\N	t
271	46	deferido	2025-04-30	AB		\N	0	0	Não	\N	t
244	83	deferido	2025-04-22	AB		\N	0	0	Não	\N	t
255	50	em_espera	2025-09-16	AB		\N	0	0	Não	\N	f
220	23	deferido	2025-04-25	AB		\N	0	0	Não	\N	t
252	60	deferido	2025-04-30	AB		\N	0	0	Não	\N	t
265	63	deferido	2025-04-25	AB		\N	0	0	Não	\N	t
240	37	deferido	2025-05-05	AB		\N	0	0	Não	\N	t
258	1	deferido	2025-04-30	BH	BH	2025-01-29	8	0	Não	\N	t
216	58	deferido	2025-04-10	TRE	TRE	\N	0	0	Não	\N	t
242	55	deferido	2025-05-05	AB		\N	0	0	Não	\N	t
270	36	deferido	2025-04-30	TRE		\N	0	0	Não	\N	t
274	83	deferido	2025-05-08	AB		\N	0	0	Não	\N	t
269	39	deferido	2025-04-28	TRE		\N	0	0	Não	\N	t
275	53	deferido	2025-05-09	AB		\N	0	0	Não	\N	t
267	21	deferido	2025-05-09	AB		\N	0	0	Não	\N	t
273	26	deferido	2025-05-08	AB		\N	0	0	Sim		t
312	51	deferido	2025-05-28	BH		\N	8	0	Não	\N	f
291	49	deferido	2025-05-29	TRE		\N	0	0	Não	\N	f
302	59	deferido	2025-05-30	AB		\N	0	0	Não	\N	f
286	19	deferido	2025-05-13	TRE		\N	0	0	Não	\N	f
278	71	deferido	2025-04-16	BH		\N	2	0	Não	\N	t
279	71	deferido	2025-04-24	BH		\N	1	0	Não	\N	t
277	50	deferido	2025-05-12	AB		\N	0	0	Não	\N	f
276	20	deferido	2025-05-06	AB		\N	0	0	Não	\N	t
280	71	deferido	2025-05-07	BH		\N	1	30	Não	\N	t
283	76	deferido	2025-05-08	TRE		\N	0	0	Não	\N	t
285	48	deferido	2025-05-14	AB		\N	0	0	Não	\N	f
282	44	deferido	2025-05-16	AB		\N	0	0	Não	\N	f
316	28	deferido	2025-05-30	TRE		\N	0	0	Não	\N	f
292	49	deferido	2025-05-30	TRE		\N	0	0	Não	\N	f
288	51	deferido	2025-05-16	BH		\N	8	0	Não	\N	f
335	60	deferido	2025-06-23	AB		\N	0	0	Não	\N	f
304	68	deferido	2025-05-30	AB		\N	0	0	Não	\N	f
336	52	deferido	2025-06-10	DS		\N	0	0	Sim		f
343	66	deferido	2025-06-30	AB		\N	0	0	Não	\N	f
344	22	deferido	2025-06-26	AB		\N	0	0	Sim		f
281	29	deferido	2025-05-16	AB		\N	0	0	Não	\N	f
297	54	deferido	2025-06-02	AB		\N	0	0	Não	\N	f
350	91	deferido	2025-06-30	AB		\N	0	0	Não	\N	f
310	32	deferido	2025-06-04	AB		\N	0	0	Não	\N	f
330	29	deferido	2025-06-06	AB		\N	0	0	Não	\N	f
307	43	deferido	2025-05-19	BH		\N	4	0	Não	\N	f
348	41	deferido	2025-06-18	AB		\N	0	0	Não	\N	f
331	53	deferido	2025-06-06	AB		\N	0	0	Não	\N	f
333	89	deferido	2025-06-09	AB		\N	0	0	Não	\N	f
334	65	deferido	2025-06-09	AB		\N	0	0	Não	\N	f
332	3	deferido	2025-06-09	AB		\N	0	0	Sim		f
347	78	deferido	2025-06-16	AB		\N	0	0	Não	\N	f
318	92	deferido	2025-06-09	AB		\N	0	0	Não	\N	f
303	59	deferido	2025-05-20	BH		\N	3	0	Não	\N	f
351	75	deferido	2025-06-16	AB		\N	0	0	Sim		f
321	39	deferido	2025-07-10	BH		\N	4	0	Não	\N	f
322	39	deferido	2025-07-11	BH		\N	4	0	Não	\N	f
323	39	deferido	2025-07-28	AB		\N	0	0	Não	\N	f
324	72	deferido	2025-06-23	AB		\N	0	0	Sim		f
325	55	deferido	2025-06-16	AB		\N	0	0	Não	\N	f
326	36	deferido	2025-06-12	TRE		\N	0	0	Não	\N	f
327	36	deferido	2025-06-13	AB		\N	0	0	Não	\N	f
328	64	deferido	2025-06-17	AB		\N	0	0	Não	\N	f
329	73	deferido	2025-06-10	AB		\N	0	0	Sim		f
294	75	deferido	2025-05-20	BH		\N	0	0	Sim		f
299	19	deferido	2025-05-20	BH		\N	8	0	Não	\N	f
317	82	deferido	2025-06-09	AB		\N	0	0	Não	\N	f
300	19	deferido	2025-06-10	AB		\N	0	0	Não	\N	t
357	3	deferido	2025-06-23	TRE		\N	0	0	Sim		f
356	68	deferido	2025-06-18	AB		\N	0	0	Não	\N	f
295	3	deferido	2025-05-23	BH		\N	8	0	Sim		f
355	59	deferido	2025-06-10	BH		\N	3	0	Não	\N	f
354	31	deferido	2025-06-16	TRE		\N	0	0	Sim		f
342	81	deferido	2025-07-11	AB		\N	0	0	Não	\N	f
289	49	deferido	2025-05-23	AB		\N	0	0	Não	\N	f
293	60	deferido	2025-05-23	AB		\N	0	0	Não	\N	f
358	50	deferido	2025-06-23	AB		\N	0	0	Não	\N	f
359	25	deferido	2025-06-30	AB		\N	0	0	Não	\N	f
296	25	deferido	2025-05-23	AB		\N	0	0	Não	\N	f
290	49	deferido	2025-05-26	TRE		\N	0	0	Não	\N	f
301	89	deferido	2025-05-26	AB		\N	0	0	Não	\N	f
298	72	deferido	2025-05-28	AB		\N	0	0	Não	\N	f
306	36	deferido	2025-05-28	AB		\N	0	0	Não	\N	f
287	43	deferido	2025-05-28	AB		\N	0	0	Não	\N	f
365	51	deferido	2025-06-27	BH		\N	8	0	Não	\N	f
363	51	deferido	2025-06-26	BH		\N	8	0	Não	\N	f
362	51	deferido	2025-06-25	BH		\N	8	0	Não	\N	f
361	51	deferido	2025-06-24	BH		\N	8	0	Não	\N	f
360	51	deferido	2025-06-23	BH		\N	8	0	Não	\N	f
349	46	deferido	2025-06-27	BH		\N	0	0	Não	\N	f
346	46	deferido	2025-06-30	AB		\N	0	0	Não	\N	f
367	89	deferido	2025-06-25	TRE		\N	0	0	Não	\N	f
369	62	deferido	2025-06-27	AB		\N	0	0	Não	\N	f
366	26	deferido	2025-07-11	AB		\N	0	0	Não	\N	f
370	23	deferido	2025-06-27	AB		\N	0	0	Sim		f
372	12	deferido	2025-06-23	BH		\N	1	20	Não	\N	f
371	47	deferido	2025-06-27	DS		\N	0	0	Não	\N	f
368	93	deferido	2025-06-27	AB		\N	0	0	Não	\N	f
373	27	deferido	2025-06-25	TRE		\N	0	0	Sim		f
385	104	deferido	2025-06-12	AB		\N	0	0	Não	\N	f
384	104	deferido	2025-07-02	AB		\N	0	0	Não	\N	f
386	25	deferido	2025-07-07	AB		\N	0	0	Não	\N	f
374	103	deferido	2025-07-04	AB		\N	0	0	Não	\N	f
377	73	deferido	2025-07-08	AB		\N	0	0	Não	\N	f
375	18	deferido	2025-06-27	BH		\N	4	0	Não	\N	f
378	2	deferido	2025-07-28	AB		\N	0	0	Não	\N	f
379	2	deferido	2025-07-10	TRE		\N	0	0	Não	\N	f
380	2	deferido	2025-07-11	TRE		\N	0	0	Não	\N	f
382	18	deferido	2025-07-11	BH		\N	8	0	Não	\N	t
381	18	deferido	2025-07-10	AB		\N	0	0	Não	\N	t
389	19	deferido	2025-07-07	BH		\N	8	0	Não	\N	f
390	43	deferido	2025-07-04	TRE		\N	0	0	Não	\N	f
391	23	deferido	2025-07-28	AB		\N	0	0	Não	\N	t
426	68	deferido	2025-07-14	AB		\N	0	0	Não	\N	t
428	68	deferido	2025-07-15	BH		\N	8	0	Não	\N	t
393	22	deferido	2025-08-01	AB		\N	0	0	Sim		f
394	22	deferido	2025-08-04	BH		\N	4	0	Sim		f
395	22	deferido	2025-08-05	BH		\N	4	0	Sim		f
396	22	deferido	2025-08-06	BH		\N	4	0	Sim		f
397	69	deferido	2025-07-30	BH		\N	5	0	Não	\N	f
398	43	deferido	2025-08-12	AB		\N	0	0	Não	\N	f
399	43	deferido	2025-07-11	BH		\N	4	0	Não	\N	f
400	49	deferido	2025-07-10	AB		\N	0	0	Não	\N	f
401	49	deferido	2025-07-11	TRE		\N	0	0	Não	\N	f
403	77	deferido	2025-07-14	AB		\N	0	0	Não	\N	f
404	56	deferido	2025-07-10	AB		\N	0	0	Não	\N	f
405	55	deferido	2025-07-11	AB		\N	0	0	Não	\N	f
406	25	deferido	2025-07-14	BH		\N	8	0	Não	\N	f
407	25	deferido	2025-07-15	BH		\N	8	0	Não	\N	f
408	25	deferido	2025-07-16	BH		\N	8	0	Não	\N	f
409	25	deferido	2025-07-17	BH		\N	8	0	Não	\N	f
410	25	deferido	2025-07-18	BH		\N	8	0	Não	\N	f
412	74	deferido	2025-07-14	BH		\N	4	0	Não	\N	f
413	74	deferido	2025-07-18	BH		\N	4	0	Não	\N	f
414	19	deferido	2025-07-14	BH		\N	8	0	Não	\N	f
411	44	deferido	2025-07-23	AB		\N	0	0	Não	\N	f
415	19	deferido	2025-07-15	BH		\N	8	0	Não	\N	f
416	19	deferido	2025-07-16	BH		\N	8	0	Não	\N	f
417	19	deferido	2025-07-17	BH		\N	8	0	Não	\N	f
418	19	deferido	2025-07-18	BH		\N	8	0	Não	\N	f
419	45	deferido	2025-07-14	BH		\N	8	0	Não	\N	f
420	45	deferido	2025-07-15	BH		\N	8	0	Não	\N	f
421	45	deferido	2025-07-16	BH		\N	8	0	Não	\N	f
422	45	deferido	2025-07-17	BH		\N	8	0	Não	\N	f
423	45	deferido	2025-07-18	BH		\N	8	0	Não	\N	f
424	74	deferido	2025-07-15	BH		\N	4	0	Não	\N	f
425	74	deferido	2025-07-16	BH		\N	4	0	Não	\N	f
512	46	deferido	2025-08-11	AB		\N	0	0	Não	\N	f
427	74	deferido	2025-07-17	BH		\N	4	0	Não	\N	f
453	68	deferido	2025-07-17	BH		\N	8	0	Não	\N	t
429	64	deferido	2025-07-14	BH		\N	8	0	Não	\N	f
430	64	deferido	2025-07-15	BH		\N	8	0	Não	\N	f
431	64	deferido	2025-07-16	BH		\N	8	0	Não	\N	f
432	64	deferido	2025-07-17	BH		\N	8	0	Não	\N	f
433	64	deferido	2025-07-18	BH		\N	8	0	Não	\N	f
434	54	deferido	2025-06-27	BH		\N	8	0	Não	\N	f
435	21	deferido	2025-07-14	BH		\N	4	0	Não	\N	f
436	21	deferido	2025-07-25	AB		\N	0	0	Não	\N	f
511	32	deferido	2025-08-01	AB		\N	0	0	Não	\N	t
445	45	deferido	2025-07-11	BH		\N	4	0	Não	\N	f
444	28	deferido	2025-07-18	TRE		\N	0	0	Não	\N	f
443	28	deferido	2025-07-17	BH		\N	8	0	Não	\N	f
442	28	deferido	2025-07-16	BH		\N	8	0	Não	\N	f
441	28	deferido	2025-07-15	BH		\N	8	0	Não	\N	f
440	28	deferido	2025-07-14	BH		\N	8	0	Não	\N	f
439	17	deferido	2025-07-25	AB		\N	0	0	Não	\N	f
438	44	deferido	2025-07-14	BH		\N	8	0	Não	\N	f
457	50	deferido	2025-07-18	BH		\N	8	0	Não	\N	f
455	76	deferido	2025-08-29	AB		\N	0	0	Não	\N	f
456	76	deferido	2025-09-01	AB		\N	0	0	Não	\N	f
507	36	deferido	2025-08-01	TRE		\N	0	0	Não	\N	t
454	68	deferido	2025-07-18	BH		\N	4	0	Não	\N	t
452	31	deferido	2025-08-19	AB		\N	0	0	Sim		f
451	20	deferido	2025-07-25	BH		\N	8	0	Não	\N	f
450	20	deferido	2025-07-21	AB		\N	0	0	Não	\N	f
449	69	deferido	2025-07-29	BH		\N	8	0	Não	\N	f
446	20	deferido	2025-07-18	BH		\N	8	0	Não	\N	f
459	29	deferido	2025-07-25	AB		\N	0	0	Não	\N	f
486	50	deferido	2025-07-30	BH		\N	0	0	Não	\N	f
482	49	em_espera	2025-09-11	TRE		\N	0	0	Não	\N	f
483	49	em_espera	2025-09-12	TRE		\N	0	0	Não	\N	f
484	49	em_espera	2025-09-19	AB		\N	0	0	Não	\N	f
485	108	deferido	2025-07-28	AB		\N	0	0	Não	\N	f
499	25	deferido	2025-07-25	BH		\N	8	0	Não	\N	f
501	12	deferido	2025-08-01	AB		\N	0	0	Não	\N	f
500	19	deferido	2025-07-25	BH		\N	8	30	Não	\N	f
504	3	deferido	2025-08-06	AB		\N	0	0	Sim		f
502	16	deferido	2025-08-11	AB		\N	0	0	Não	\N	f
503	53	deferido	2025-08-01	AB		\N	0	0	Não	\N	f
505	59	deferido	2025-08-04	AB		\N	0	0	Não	\N	f
402	23	deferido	2025-07-11	BH		\N	4	0	Não	\N	t
508	65	deferido	2025-08-01	AB		\N	0	0	Não	\N	f
509	93	deferido	2025-08-29	AB		\N	0	0	Não	\N	f
506	47	deferido	2025-08-01	BH		\N	4	0	Não	\N	f
510	93	deferido	2025-09-01	TRE		\N	0	0	Não	\N	f
514	26	deferido	2025-08-29	AB		\N	0	0	Sim		f
515	74	deferido	2025-08-15	AB		\N	0	0	Não	\N	f
392	43	deferido	2025-07-10	AB		\N	0	0	Não	\N	t
516	75	deferido	2025-08-11	AB		\N	0	0	Não	\N	f
437	32	deferido	2025-07-11	AB		\N	0	0	Não	\N	t
518	17	deferido	2025-08-29	AB		\N	0	0	Não	\N	f
513	18	deferido	2025-08-25	AB		\N	0	0	Não	\N	f
517	36	deferido	2025-08-07	BH		\N	3	3	Não	\N	t
522	74	deferido	2025-08-06	BH		\N	4	0	Não	\N	f
525	1	deferido	2025-08-06	BH		\N	3	0	Não	\N	f
521	73	deferido	2025-08-01	BH		\N	4	0	Não	\N	f
524	112	deferido	2025-08-08	AB		\N	0	0	Não	\N	f
520	25	deferido	2025-07-28	BH		\N	4	0	Não	\N	f
519	52	deferido	2025-08-12	AB		\N	0	0	Sim		f
523	59	deferido	2025-08-06	BH		\N	2	0	Não	\N	f
526	20	deferido	2025-07-24	BH		\N	5	0	Não	\N	f
532	21	deferido	2025-08-12	BH		\N	4	0	Não	\N	f
531	19	deferido	2025-08-08	BH		\N	4	0	Não	\N	f
529	73	deferido	2025-08-12	AB		\N	0	0	Não	\N	f
528	16	deferido	2025-08-22	TRE		\N	0	0	Não	\N	f
530	48	deferido	2025-08-08	AB		\N	0	0	Não	\N	f
537	28	deferido	2025-08-29	AB		\N	0	0	Não	\N	f
535	60	deferido	2025-08-15	AB		\N	0	0	Não	\N	f
527	76	deferido	2025-08-12	TRE		\N	0	0	Não	\N	f
533	76	deferido	2025-08-06	BH		\N	5	0	Não	\N	f
538	81	deferido	2025-08-15	AB		\N	0	0	Não	\N	f
534	45	deferido	2025-08-15	BH		\N	4	0	Não	\N	f
539	72	deferido	2025-08-29	BH		\N	4	0	Não	\N	f
536	89	deferido	2025-08-14	AB		\N	0	0	Não	\N	f
541	89	deferido	2025-08-15	BH		\N	8	0	Não	\N	f
545	19	deferido	2025-08-15	TRE		\N	0	0	Não	\N	f
544	19	deferido	2025-08-13	BH		\N	4	0	Não	\N	f
542	59	deferido	2025-08-15	TRE		\N	0	0	Não	\N	f
546	66	deferido	2025-08-15	AB		\N	0	0	Não	\N	f
547	18	deferido	2025-08-22	BH		\N	4	0	Sim		f
550	2	em_espera	2025-08-25	AB		\N	0	0	Não	\N	f
549	19	deferido	2025-08-18	TRE		\N	0	0	Não	\N	f
548	82	deferido	2025-08-20	AB		\N	0	0	Não	\N	f
552	25	em_espera	2025-08-29	AB		\N	0	0	Não	\N	f
553	39	em_espera	2025-09-08	AB		\N	0	0	Não	\N	f
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: folgas_user
--

COPY public.alembic_version (version_num) FROM stdin;
ccfff68c77d4
\.


--
-- Data for Name: banco_de_horas; Type: TABLE DATA; Schema: public; Owner: folgas_user
--

COPY public.banco_de_horas (id, funcionario_id, horas, minutos, total_minutos, data_realizacao, status, data_criacao, data_atualizacao, motivo, usufruido) FROM stdin;
5	1	24	0	1440	2025-01-29	Deferido	2025-02-01 20:22:08.082121	2025-02-01 20:22:17.958043	Saldo de férias	f
10	18	8	0	480	2025-02-05	Deferido	2025-02-03 13:04:01.47491	2025-02-03 13:04:59.126135	FOLGA SEPROS	f
11	18	8	0	480	2025-02-17	Deferida	2025-02-03 13:07:17.645922	2025-02-03 13:07:17.650366	BH	f
12	19	1	0	60	2025-02-02	Deferido	2025-02-03 13:27:25.615211	2025-02-03 13:27:53.622901	Reunião	f
13	12	1	0	60	2025-01-07	Deferido	2025-02-03 13:38:29.120826	2025-02-03 15:02:13.959153	Fechar a escola, atendimento 	f
14	12	1	0	60	2025-01-08	Deferido	2025-02-03 13:39:05.570667	2025-02-03 15:02:15.55862	Atendimento, fechamento 	f
15	12	1	20	80	2025-01-13	Deferido	2025-02-03 13:39:38.039047	2025-02-03 15:02:17.437929	Atendimento 	f
16	12	1	0	60	2025-01-24	Indeferido	2025-02-03 13:50:58.820976	2025-02-03 15:02:42.056013	Atendimento, documentação 	f
17	12	2	25	145	2025-01-31	Deferido	2025-02-03 13:51:42.429959	2025-02-03 15:02:49.619113	Documentação 	f
18	12	1	0	60	2025-01-23	Deferido	2025-02-03 15:06:00.421761	2025-02-03 15:07:06.230196	Atendimento 	f
19	12	1	20	80	2025-02-03	Deferida	2025-02-03 17:07:30.420344	2025-02-03 17:07:30.426336	BH	f
20	1	1	10	70	2025-02-03	Deferido	2025-02-03 19:22:16.561118	2025-02-03 19:22:26.076014	Atendimento secretaria	f
21	37	2	8	128	2025-02-04	Deferido	2025-02-05 21:45:41.708623	2025-02-06 20:20:11.679795	Limpeza da escola	f
22	30	13	30	810	2024-09-28	Deferido	2025-02-05 22:28:12.545202	2025-02-06 20:20:39.668657	Referente a 9 horas trabalhadas mais 50%	f
23	30	18	0	1080	2024-09-29	Deferido	2025-02-05 22:31:14.64363	2025-02-06 20:20:49.95231	Referente a 9 horas trabalhadas +100%	f
24	30	8	0	480	2024-10-06	Deferido	2025-02-05 22:33:09.427782	2025-02-06 20:20:59.259003	Referente a 4 horas+ 100%	f
25	1	1	0	60	2025-02-05	Deferido	2025-02-06 10:57:55.631101	2025-02-06 20:21:00.777831	Malote SEDUC	f
26	12	1	5	65	2025-02-05	Deferido	2025-02-06 19:25:50.656454	2025-02-06 20:21:03.10872	Documentação 	f
27	20	1	5	65	2025-02-06	Deferido	2025-02-07 18:01:23.238648	2025-02-07 18:03:31.478138	Documentação Prestação de contas PDDE	f
28	37	2	8	128	2025-02-07	Deferida	2025-02-07 18:21:24.23189	2025-02-07 18:21:24.238349	BH	f
29	30	8	0	480	2025-03-07	Deferida	2025-02-08 15:40:19.309508	2025-02-08 15:40:19.316299	BH	f
30	19	0	30	30	2025-02-06	Deferido	2025-02-10 11:02:33.87756	2025-02-11 02:52:40.643919	HTL/ não era para fazer	f
31	19	0	30	30	2025-02-07	Deferido	2025-02-10 11:03:11.211844	2025-02-11 02:52:41.728887	HTL/ não era para fazer	f
32	20	1	30	90	2025-02-19	Deferido	2025-02-21 13:20:16.26487	2025-02-21 23:58:27.348382	Reuniaõ CAE	f
33	20	0	40	40	2025-02-20	Deferido	2025-02-21 13:22:46.689566	2025-02-21 23:58:28.695377	Controle de Estoque e  envio de SAUs	f
35	65	0	0	0	2025-03-06	Deferida	2025-03-07 13:30:58.655782	2025-03-07 13:30:58.660914	BH	f
36	65	0	0	0	2025-03-07	Deferida	2025-03-07 13:31:00.440936	2025-03-07 13:31:00.444318	BH	f
34	66	4	20	260	2025-02-12	Deferido	2025-03-06 18:03:24.204205	2025-03-07 13:32:38.092902	Fiquei pra ajudar a Tita 	f
43	51	15	30	930	2024-10-06	Deferido	2025-03-11 17:59:11.129585	2025-03-12 00:37:16.783637	Eleição 	f
44	51	8	30	510	2024-11-12	Deferido	2025-03-11 18:01:37.736663	2025-03-12 00:37:17.980529	Cobrir funcionário que faltou	f
37	46	2	30	150	2025-02-22	Deferido	2025-03-10 14:43:08.080659	2025-03-12 00:37:18.993083	Dedetização 	f
38	46	2	30	150	2025-02-08	Deferido	2025-03-10 14:44:52.342543	2025-03-12 00:37:20.429374	Dedetização 	f
39	62	4	0	240	2025-02-12	Deferido	2025-03-11 11:15:41.70359	2025-03-12 00:37:21.61439	Comprimento de 4h participação reunião d	f
40	51	7	20	440	2024-08-15	Deferido	2025-03-11 17:50:43.155822	2025-03-12 00:37:22.683852	(Evento) Cinema na escola 	f
41	51	10	30	630	2024-10-06	Deferido	2025-03-11 17:54:59.123982	2025-03-12 00:37:24.123064	Faxina para eleição 	f
42	51	10	30	630	2024-10-05	Deferido	2025-03-11 17:57:02.863874	2025-03-12 00:37:25.333405	Faxina eleição 	f
45	51	8	0	480	2024-11-19	Deferido	2025-03-11 18:02:35.830972	2025-03-12 00:37:26.672631	Evento	f
46	51	8	0	480	2024-12-12	Deferido	2025-03-11 18:04:37.155558	2025-03-12 00:37:27.652458	Formatura	f
47	51	2	0	120	2025-02-28	Deferido	2025-03-11 18:05:26.443252	2025-03-12 00:37:28.599485	Hora extra	f
51	51	8	0	480	2025-03-19	Deferida	2025-03-13 21:12:26.181344	2025-03-13 21:12:26.192954	BH	f
48	29	1	20	80	2025-02-20	Indeferido	2025-03-13 17:09:10.705451	2025-03-14 20:43:24.863247	Hora extra 	f
49	46	8	0	480	2024-12-12	Indeferido	2025-03-13 17:11:10.491364	2025-03-14 20:43:27.79609	Formatura 	f
50	29	1	0	60	2025-03-13	Deferido	2025-03-13 19:25:53.577177	2025-03-14 20:43:29.809103	Hora extra	f
52	29	8	0	480	2025-03-13	Deferido	2025-03-14 20:42:25.756969	2025-03-14 20:43:34.877961	Acordo com Rafael 	f
53	29	8	0	480	2025-03-28	Deferida	2025-03-14 20:44:48.451457	2025-03-14 20:44:48.455642	BH	f
54	71	3	1	181	2025-03-19	Deferido	2025-03-20 18:30:27.71025	2025-03-21 00:21:39.060063	Não teve funcionário a noite para cobrir	f
55	20	2	30	150	2025-03-24	Deferido	2025-03-25 17:35:56.35016	2025-03-26 20:47:37.142922	COBERTURA DE GREVE	f
56	20	1	25	85	2025-03-18	Deferido	2025-03-25 17:38:43.887506	2025-03-26 20:47:38.00935	APM (bancos bradesco e Brasil)	f
57	51	8	0	480	2025-03-31	Deferida	2025-04-05 23:51:02.439122	2025-04-05 23:51:02.446326	BH	f
58	1	8	0	480	2025-04-14	Deferida	2025-04-11 15:54:16.398713	2025-04-11 15:54:16.703203	BH	f
59	1	8	0	480	2025-04-14	Deferida	2025-04-11 15:56:33.857879	2025-04-11 15:56:33.864176	BH	f
60	12	1	0	60	2025-04-14	Deferido	2025-04-15 00:43:55.140589	2025-04-19 16:59:21.19892	Páscoa 	f
61	71	2	25	145	2025-04-15	Deferido	2025-04-16 14:09:45.945482	2025-04-19 16:59:22.86741	Greve dos servidores.	f
63	1	8	0	480	2025-04-30	Deferida	2025-04-24 02:33:18.620615	2025-04-24 02:33:18.629619	BH	f
62	50	2	30	150	2025-04-23	Deferido	2025-04-23 22:22:36.2003	2025-04-24 02:34:20.601998	Pagamento de greve	f
64	1	3	0	180	2025-04-22	Deferido	2025-04-24 02:34:08.934883	2025-04-24 02:34:23.443106	Acertos nas Papeletas	f
65	50	2	37	157	2025-04-24	Deferido	2025-04-24 21:38:27.854509	2025-05-08 16:19:09.833415	Pagamento de greve	f
66	50	0	30	30	2025-02-14	Deferido	2025-04-24 21:50:23.280917	2025-05-08 16:19:12.969887	Pagamento de greve 	f
67	50	1	16	76	2025-04-04	Deferido	2025-04-24 21:51:59.203766	2025-05-08 16:19:15.270808	Pagamento de greve 	f
68	50	0	30	30	2025-04-07	Deferido	2025-04-24 21:53:24.954637	2025-05-08 16:19:17.801142	Pagamento de greve 	f
69	50	2	30	150	2025-04-25	Deferido	2025-04-29 02:03:41.814692	2025-05-08 16:19:22.967693	Pagamento de greve 	f
70	50	3	2	182	2025-04-28	Deferido	2025-04-29 02:04:52.984017	2025-05-08 16:19:26.714974	Pagamento de greve 	f
71	46	3	0	180	2025-04-15	Deferido	2025-04-29 12:37:25.557233	2025-05-08 16:19:29.159772	Bolo páscoa 	f
72	50	2	32	152	2025-04-30	Deferido	2025-05-01 18:02:12.956765	2025-05-08 16:19:34.81282	Cobrindo  funcionaria faltosa	f
73	71	1	30	90	2025-05-07	Deferida	2025-05-08 18:07:46.682995	2025-05-08 18:07:46.69117	BH	f
74	71	1	0	60	2025-04-24	Deferida	2025-05-08 18:08:04.305996	2025-05-08 18:08:04.310809	BH	f
75	71	2	0	120	2025-04-16	Deferida	2025-05-08 18:08:06.380071	2025-05-08 18:08:06.385484	BH	f
76	50	0	30	30	2025-05-08	Deferido	2025-05-09 10:55:29.105973	2025-05-09 23:13:45.063055	Preparação  do dia de quem cuida de mim 	f
81	51	8	0	480	2025-05-16	Deferida	2025-05-19 14:00:39.167574	2025-05-19 14:00:39.176623	BH	f
78	50	1	10	70	2025-05-13	Deferido	2025-05-13 20:22:45.998825	2025-05-19 18:07:00.043474	Preparando decoração  para o dia de de m	f
79	50	4	0	240	2025-05-15	Deferido	2025-05-15 23:43:36.952054	2025-05-19 18:07:01.11775	Fazendo  declaração  do dia de quem  de 	f
80	50	4	0	240	2025-05-16	Deferido	2025-05-17 10:29:54.84035	2025-05-19 18:07:02.934051	Organização  do dia de quem cuida de mim	f
77	71	1	59	119	2025-05-08	Deferido	2025-05-13 18:17:14.888193	2025-05-19 18:06:58.052382	Não veio um funcionário.	f
82	75	0	0	0	2025-05-20	Deferida	2025-05-19 18:07:40.161399	2025-05-19 18:07:40.165593	BH	f
83	3	8	0	480	2025-05-17	Deferido	2025-05-19 18:26:33.522035	2025-05-19 18:26:49.602818	Dia de quem cuida de mim	f
84	3	8	0	480	2025-05-23	Deferida	2025-05-19 20:03:32.676571	2025-05-19 20:03:32.688457	BH	f
85	59	8	0	480	2025-05-17	Deferido	2025-05-20 11:20:17.661407	2025-05-21 19:34:18.526126	Evento	f
86	19	8	0	480	2025-05-17	Indeferido	2025-05-21 19:28:21.878482	2025-05-21 19:34:20.946443	Festa"QUEM CUIDA DE MIM"	f
87	19	8	0	480	2025-05-17	Deferido	2025-05-21 19:29:31.841086	2025-05-21 19:34:26.374726	Festa"QUEM CUIDA DE MIM"	f
88	19	8	0	480	2025-05-20	Deferida	2025-05-21 20:02:36.502539	2025-05-21 20:02:36.508106	BH	f
89	25	2	0	120	2025-05-21	Deferido	2025-05-22 00:43:48.279933	2025-05-22 17:29:49.552975	Confecção decoração festa junina.	f
90	28	2	0	120	2025-05-21	Deferido	2025-05-22 15:22:31.01417	2025-05-22 17:29:51.190108	Confecção decoração da festa junina 	f
91	59	3	0	180	2025-05-20	Deferida	2025-05-22 17:30:13.187877	2025-05-22 17:30:13.193897	BH	f
92	25	2	0	120	2025-05-22	Deferido	2025-05-22 23:08:21.4328	2025-05-23 15:46:24.410658	Confecção decoração festa junina.	f
93	43	8	0	480	2025-05-17	Deferido	2025-05-26 16:26:44.761382	2025-05-26 16:30:20.315175	Festa dia de quem cuida de mim	f
94	43	4	0	240	2025-05-19	Deferida	2025-05-26 17:33:54.743896	2025-05-26 17:33:54.751126	BH	f
95	25	2	0	120	2025-05-26	Deferido	2025-05-27 00:19:40.451559	2025-05-27 00:47:19.838286	Confecção decoração festa junina.	f
99	51	8	0	480	2025-05-28	Deferida	2025-05-27 16:14:24.172465	2025-05-27 16:14:24.179417	BH	f
96	28	1	0	60	2025-05-26	Deferido	2025-05-27 10:52:16.322838	2025-06-02 16:28:50.898323	Confecção decorativa festa junina	f
97	2	8	0	480	2025-05-17	Deferido	2025-05-27 13:27:31.064759	2025-06-02 16:28:54.664323	Dia de quem cuida	f
98	28	8	0	480	2025-05-17	Deferido	2025-05-27 15:30:27.834421	2025-06-02 16:28:56.917125	Dia das mães 	f
100	25	2	0	120	2025-05-27	Deferido	2025-05-27 22:58:43.468763	2025-06-02 16:29:01.154391	Confecção decoração festa junina.	f
101	28	1	0	60	2025-05-27	Deferido	2025-05-28 13:15:53.468463	2025-06-02 16:29:02.083019	Confecção festa junina	f
102	50	3	3	183	2025-05-29	Deferido	2025-05-29 23:36:09.33253	2025-06-02 16:29:02.852642	Fazendo  decoração  da festa  junina	f
103	25	3	0	180	2025-05-29	Deferido	2025-05-30 01:56:55.545635	2025-06-02 16:29:03.89122	Confecção decoração festa junina.	f
104	19	2	0	120	2025-05-21	Deferido	2025-05-30 16:17:56.480157	2025-06-02 16:29:04.575767	Decoração festa junina 	f
105	19	2	0	120	2025-05-21	Deferido	2025-05-30 16:18:17.448963	2025-06-02 16:29:05.255215	Decoração festa junina 	f
106	19	2	0	120	2025-05-22	Deferido	2025-05-30 16:19:18.35196	2025-06-02 16:29:06.846392	Decoração festa junina 	f
107	19	2	0	120	2025-05-26	Deferido	2025-05-30 16:20:39.338774	2025-06-02 16:29:08.405866	Decoração festa junina 	f
108	19	2	0	120	2025-05-27	Deferido	2025-05-30 16:21:10.525701	2025-06-02 16:29:10.402618	Decoração festa junina 	f
109	19	3	0	180	2025-05-29	Deferido	2025-05-30 16:21:43.947969	2025-06-02 16:29:11.280591	Decoração festa junina 	f
110	21	2	0	120	2025-05-27	Deferido	2025-05-30 16:56:01.159808	2025-06-02 16:29:13.072434	Preparo festa	f
111	21	1	0	60	2025-05-29	Deferido	2025-05-30 16:56:25.438085	2025-06-02 16:29:14.927292	Preparo festa	f
112	45	3	40	220	2025-05-16	Deferido	2025-06-02 14:09:31.290776	2025-06-02 16:29:15.970076	Organização ( dia de quem cuida de mim)	f
113	45	5	45	345	2025-05-17	Deferido	2025-06-02 14:10:18.712473	2025-06-02 16:29:17.122183	Festa Dia de quem cuida de mim	f
114	45	2	0	120	2025-05-26	Deferido	2025-06-02 14:11:02.873929	2025-06-02 16:29:18.127592	Organização (Festa Julina)	f
115	74	2	0	120	2025-05-21	Deferido	2025-06-02 14:47:43.679405	2025-06-02 16:29:21.19196	Montagem da ornamentação da festa junina	f
116	39	8	0	480	2025-05-17	Deferido	2025-06-02 15:36:09.124985	2025-06-02 16:29:22.683497	Dia de quem cuida de mim (sábado)	f
117	74	8	0	480	2025-05-17	Deferido	2025-06-02 18:18:15.65054	2025-06-03 14:53:36.538073	Dia de quem cuida de mim 	f
118	74	8	0	480	2025-05-17	Deferido	2025-06-02 18:18:16.017577	2025-06-03 14:53:37.791628	Dia de quem cuida de mim 	f
119	64	3	6	186	2025-05-28	Deferido	2025-06-02 23:35:15.543504	2025-06-03 14:54:22.821527	Decoração festa junina	f
120	64	2	36	156	2025-05-28	Deferido	2025-06-02 23:39:40.643096	2025-06-03 14:54:33.12888	Decoração festa junina	f
121	64	2	0	120	2025-05-22	Deferido	2025-06-02 23:48:13.619302	2025-06-03 14:55:29.533803	Decoração festa junina	f
122	64	6	0	360	2025-05-17	Deferido	2025-06-02 23:49:59.969881	2025-06-03 14:55:30.477495	Dia de quem cuida de mim	f
123	64	3	40	220	2025-05-16	Deferido	2025-06-02 23:52:46.092441	2025-06-03 14:55:49.076216	Decoração dia de quem cuida de mim	f
124	64	2	43	163	2025-05-13	Deferido	2025-06-02 23:55:04.010418	2025-06-03 14:55:50.155636	Decoração dia de quem cuida de mim	f
125	64	1	42	102	2025-05-12	Deferido	2025-06-03 00:00:02.141225	2025-06-03 14:55:51.0673	Decoração dia de quem cuida de mim	f
126	73	2	0	120	2025-05-17	Deferido	2025-06-03 14:15:08.012917	2025-06-03 14:55:51.994113	Quem cuida de mim	f
127	39	4	0	240	2025-07-10	Deferida	2025-06-03 15:03:06.506026	2025-06-03 15:03:06.512802	BH	f
128	39	4	0	240	2025-07-11	Deferida	2025-06-03 15:03:11.304367	2025-06-03 15:03:11.310435	BH	f
129	45	3	0	180	2025-05-17	Deferido	2025-06-03 15:05:34.952878	2025-06-03 23:01:22.388792	Dia de quem cuida de mim(50%)	f
130	68	2	30	150	2025-05-16	Deferido	2025-06-03 15:49:17.264494	2025-06-03 23:01:26.751615	Dia das mães 	f
131	68	7	30	450	2025-05-17	Deferido	2025-06-03 15:50:04.938101	2025-06-03 23:01:30.036593	Dia das mães 	f
132	64	3	0	180	2025-05-17	Deferido	2025-06-03 17:40:35.922232	2025-06-03 23:01:37.048331	Dia de quem cuida de mim	f
133	79	9	0	540	2025-05-17	Indeferido	2025-06-04 13:34:47.462454	2025-06-05 11:33:29.582801	Dia de quem cuida	f
134	51	3	30	210	2025-02-14	Deferido	2025-06-04 14:41:51.254845	2025-06-05 11:33:37.349388	Faxina	f
135	51	4	30	270	2025-03-19	Indeferido	2025-06-04 14:49:06.023879	2025-06-05 11:33:42.265581	Evento eja	f
136	51	4	0	240	2025-04-05	Indeferido	2025-06-04 17:17:06.92967	2025-06-05 11:35:07.317062	Detetizacao 	f
137	51	2	18	138	2025-04-15	Deferido	2025-06-04 17:19:39.529493	2025-06-05 11:35:23.977138	Hora extra	f
138	51	2	30	150	2025-04-22	Deferido	2025-06-04 17:20:30.007756	2025-06-05 11:35:31.876034	Hora extra	f
139	18	10	0	600	2025-05-17	Deferido	2025-06-04 21:39:21.32956	2025-06-05 11:36:03.675256	Dia da família 	f
141	51	7	24	444	2025-06-03	Deferido	2025-06-06 18:32:29.401809	2025-06-18 18:16:02.826458	Cobrir funcionários 	f
142	51	3	4	184	2025-06-04	Deferido	2025-06-06 18:35:32.825766	2025-06-18 18:16:05.442816	Cobrir funcionário 	f
143	51	3	0	180	2025-04-05	Deferido	2025-06-06 18:36:08.953052	2025-06-18 18:16:07.292927	Detetizacao 	f
144	22	8	0	480	2025-05-17	Deferido	2025-06-06 22:39:59.768238	2025-06-18 18:16:09.042418	Festa "Quem cuida de mim"	f
145	50	0	40	40	2025-06-06	Deferido	2025-06-07 11:11:52.198963	2025-06-18 18:16:10.903687	Reunião  com a diretoria 	f
146	46	7	20	440	2025-05-17	Deferido	2025-06-09 13:02:08.517822	2025-06-18 18:16:12.601106	Dia de quem cuida de mim 	f
147	46	6	20	380	2025-05-24	Deferido	2025-06-09 13:03:24.753759	2025-06-18 18:16:14.18786	Manutenção 	f
148	62	22	30	1350	2025-05-05	Deferido	2025-06-10 16:22:12.323738	2025-06-18 18:16:15.870044	1h30 feita 05/05 até 23/05 e 28/05 3h15	f
149	62	3	45	225	2025-05-28	Deferido	2025-06-10 16:22:53.186707	2025-06-18 18:16:17.829921	1h30 feita 05/05 até 23/05 e 28/05 3h15	f
150	59	1	0	60	2025-04-11	Deferido	2025-06-12 14:43:18.443904	2025-06-18 18:16:19.322711	Hora extra faxina 	f
151	59	3	0	180	2025-06-10	Deferida	2025-06-16 13:52:03.235213	2025-06-16 13:52:03.252324	BH	f
140	79	9	0	540	2025-05-17	Deferido	2025-06-05 11:45:17.182908	2025-06-18 18:16:00.637864	Festa do dia de quem cuida 	f
152	45	2	30	150	2025-06-16	Deferido	2025-06-16 23:21:53.259503	2025-06-18 18:16:21.102838	Organização festa julina	f
153	50	3	2	182	2025-06-16	Deferido	2025-06-17 07:17:48.862765	2025-06-18 18:16:23.001095	Fazendo a decoração para festa da escola	f
154	25	2	30	150	2025-06-16	Deferido	2025-06-17 10:22:12.330116	2025-06-18 18:16:24.776924	Confecção decoração festa junina.	f
155	19	2	30	150	2025-06-16	Deferido	2025-06-17 16:46:23.614791	2025-06-18 18:16:26.43583	Decoração festa junina 	f
156	50	2	28	148	2025-06-17	Deferido	2025-06-17 22:34:01.255835	2025-06-18 18:16:27.780468	Organização  e construção  de enfeites  	f
157	45	2	30	150	2025-06-17	Deferido	2025-06-17 23:42:06.595878	2025-06-18 18:16:29.134572	Organização festa julina	f
158	25	2	30	150	2025-06-17	Deferido	2025-06-18 10:36:04.770269	2025-06-18 18:16:30.556707	Confecção decoração festa junina.	f
159	51	8	0	480	2025-06-27	Deferida	2025-06-18 18:17:17.878847	2025-06-18 18:17:17.885773	BH	f
160	51	8	0	480	2025-06-26	Deferida	2025-06-18 18:17:19.781346	2025-06-18 18:17:19.786738	BH	f
161	51	8	0	480	2025-06-25	Deferida	2025-06-18 18:17:21.295589	2025-06-18 18:17:21.300919	BH	f
162	51	8	0	480	2025-06-24	Deferida	2025-06-18 18:17:22.765029	2025-06-18 18:17:22.770698	BH	f
163	51	8	0	480	2025-06-23	Deferida	2025-06-18 18:17:24.496828	2025-06-18 18:17:24.506457	BH	f
164	46	0	0	0	2025-06-27	Deferida	2025-06-18 18:17:58.027571	2025-06-18 18:17:58.030773	BH	f
165	25	2	0	120	2025-06-18	Deferido	2025-06-18 22:56:28.159248	2025-06-23 15:19:30.473247	Confecção decoração festa junina.	f
166	50	4	0	240	2025-06-18	Deferido	2025-06-19 00:38:08.027106	2025-06-23 15:19:51.888267	Fazendo  decoração de festa junina 	f
167	45	2	0	120	2025-06-18	Deferido	2025-06-19 00:46:38.852023	2025-06-23 15:19:54.420525	Organização festa julina	f
168	26	8	0	480	2025-05-17	Deferido	2025-06-21 23:57:43.376427	2025-06-23 15:21:38.609621	Participação no evento "Quem Cuida de m"	f
169	89	4	0	240	2025-06-05	Deferido	2025-06-23 10:50:59.510897	2025-06-23 15:22:32.954653	Conselho de escola	f
170	31	8	0	480	2025-05-17	Deferido	2025-06-23 10:51:14.264772	2025-06-23 15:22:34.620526	Dia de quem cuida de mim	f
171	89	1	0	60	2025-06-13	Deferido	2025-06-23 10:51:53.888076	2025-06-23 15:23:02.663733	Conselho de classe	f
172	31	1	1	61	2025-06-05	Deferido	2025-06-23 10:52:16.373275	2025-06-23 15:23:05.217254	Pagamento da greve	f
173	31	1	1	61	2025-06-18	Deferido	2025-06-23 10:52:44.899975	2025-06-23 15:23:06.527275	Pagamento de greve	f
174	18	4	10	250	2024-10-09	Deferido	2025-06-23 12:04:25.721311	2025-06-23 15:23:07.368762	Arrumação da mostra cultural.	f
178	12	1	20	80	2025-06-23	Deferida	2025-06-24 16:23:36.545282	2025-06-24 16:23:36.551626	BH	f
175	19	2	30	150	2025-06-16	Deferido	2025-06-24 16:21:47.184014	2025-07-02 12:47:43.074988	Decoração festa junina 	f
176	19	2	30	150	2025-06-17	Deferido	2025-06-24 16:22:05.386066	2025-07-02 12:47:48.296739	Decoração festa junina 	f
177	19	2	0	120	2025-06-18	Deferido	2025-06-24 16:22:40.243341	2025-07-02 12:47:49.909462	Decoração festa junina 	f
179	50	4	25	265	2025-06-24	Deferido	2025-06-24 23:27:53.300355	2025-07-02 12:47:52.204416	Fazendo  decoração  festa junina 	f
180	25	3	0	180	2025-06-24	Deferido	2025-06-25 02:21:39.959274	2025-07-02 12:47:54.22223	Confecção decoração festa junina.	f
181	50	4	1	241	2025-06-25	Deferido	2025-06-25 23:15:35.59538	2025-07-02 12:47:55.903813	Decoração  da festa  junina 	f
182	45	2	52	172	2025-06-25	Deferido	2025-06-25 23:34:08.041961	2025-07-02 12:47:58.070464	Organização festa julina	f
183	25	3	0	180	2025-06-25	Deferido	2025-06-26 10:13:03.211875	2025-07-02 12:47:59.672325	Confecção decoração festa junina.	f
184	20	5	25	325	2025-05-17	Deferido	2025-06-26 15:23:34.78268	2025-07-02 12:48:01.661789	Dia de quem cuida de mim.	f
185	21	2	0	120	2025-06-26	Deferido	2025-06-26 22:43:54.114241	2025-07-02 12:48:03.585626	Preparativos festa	f
186	50	4	0	240	2025-06-26	Deferido	2025-06-26 23:04:30.50212	2025-07-02 12:48:04.707427	Fazendo decoração de festa junina	f
187	25	3	0	180	2025-06-26	Deferido	2025-06-27 01:16:17.585818	2025-07-02 12:48:05.847534	Confecção decoração festa junina.	f
188	45	3	0	180	2025-06-26	Deferido	2025-06-27 09:30:59.267793	2025-07-02 12:48:06.951029	Organização festa julina	f
189	19	2	0	120	2025-06-24	Deferido	2025-06-27 16:01:56.5135	2025-07-02 12:48:08.032606	Decoração festa junina 	f
190	19	2	0	120	2025-06-25	Deferido	2025-06-27 16:02:10.286408	2025-07-02 12:48:09.207074	Decoração festa junina 	f
191	19	2	0	120	2025-06-26	Deferido	2025-06-27 16:02:27.100856	2025-07-02 12:48:10.165628	Decoração festa junina 	f
192	28	2	46	166	2025-06-17	Deferido	2025-06-27 16:06:55.297567	2025-07-02 12:48:11.036205	Confecção festa junina	f
193	50	2	17	137	2025-06-27	Deferido	2025-06-27 21:49:05.185928	2025-07-02 12:48:11.864814	Anotações  de prendas e enfeites de fest	f
194	45	1	43	103	2025-06-27	Deferido	2025-06-27 23:45:09.902854	2025-07-02 12:48:12.63585	Organização festa julina	f
195	25	3	0	180	2025-06-27	Deferido	2025-06-28 00:10:10.464772	2025-07-02 12:48:13.34244	Confecção decoração festa junina.	f
196	21	2	0	120	2025-06-27	Deferido	2025-06-28 00:40:54.078121	2025-07-02 12:48:14.113609	Preparativos festa	f
197	45	2	15	135	2025-06-30	Deferido	2025-07-01 00:32:51.073691	2025-07-02 12:48:14.887792	Organização festa julina	f
198	19	3	0	180	2025-06-27	Deferido	2025-07-01 16:20:20.397653	2025-07-02 12:48:15.876905	Decoração festa junina 	f
199	19	3	0	180	2025-06-30	Deferido	2025-07-01 16:26:11.4725	2025-07-02 12:48:16.889503	Decoração festa junina 	f
200	19	1	0	60	2025-06-24	Deferido	2025-07-01 16:28:32.980051	2025-07-02 12:48:17.76447	Decoração festa junina 	f
201	19	1	0	60	2025-06-25	Deferido	2025-07-01 16:28:48.012188	2025-07-02 12:48:18.625613	Decoração festa junina 	f
202	19	1	0	60	2025-06-26	Deferido	2025-07-01 16:28:59.202769	2025-07-02 12:48:19.384188	Decoração festa junina 	f
203	21	2	0	120	2025-06-30	Deferido	2025-07-01 18:08:52.293738	2025-07-02 12:48:20.386657	Preparo festa	f
204	45	2	30	150	2025-07-01	Deferido	2025-07-01 23:10:15.240937	2025-07-02 12:48:21.253781	Organização festa Julina	f
205	25	2	30	150	2025-07-01	Deferido	2025-07-02 01:27:16.68853	2025-07-02 12:48:22.17689	Confecção decoração festa junina.	f
206	1	2	30	150	2025-07-01	Deferido	2025-07-02 12:46:42.620129	2025-07-02 12:48:22.931558	Conselho EJA	f
208	74	1	38	98	2025-07-01	Deferido	2025-07-02 14:00:12.513464	2025-07-07 10:53:54.35101	Festa junina 	f
209	74	1	33	93	2025-06-30	Deferido	2025-07-02 14:04:43.065338	2025-07-07 10:53:56.723968	Decoração festa junina	f
210	21	2	0	120	2025-07-01	Deferido	2025-07-02 16:46:05.268298	2025-07-07 10:54:01.785792	Preparo festa	f
211	28	2	30	150	2025-07-01	Deferido	2025-07-02 17:10:07.356848	2025-07-07 10:54:03.253353	Confecção da festa junina	f
212	50	4	7	247	2025-06-30	Deferido	2025-07-02 23:38:45.209289	2025-07-07 10:54:04.590157	Fazer  decoração  de festa 	f
213	50	4	7	247	2025-06-30	Deferido	2025-07-02 23:39:21.013583	2025-07-07 10:54:05.672273	Fazer  decoração  de festa 	f
214	45	3	4	184	2025-07-02	Deferido	2025-07-02 23:42:18.275351	2025-07-07 10:54:13.401494	Organização festa julina	f
215	50	3	44	224	2025-07-02	Indeferido	2025-07-02 23:43:43.906845	2025-07-07 10:54:17.037228	Fazer  decoração  de festa 	f
216	74	3	0	180	2025-07-02	Deferido	2025-07-02 23:47:44.658782	2025-07-07 10:54:18.475992	Decoração festa junina 	f
217	25	3	0	180	2025-07-02	Deferido	2025-07-03 10:04:12.308973	2025-07-07 10:54:19.704927	Confecção decoração festa junina.	f
218	64	3	0	180	2025-05-29	Deferido	2025-07-03 12:51:10.936227	2025-07-07 10:54:20.875069	Decoração festa junina	f
241	18	4	0	240	2025-06-27	Deferida	2025-07-07 00:17:47.024656	2025-07-07 00:17:47.034379	BH	f
242	19	8	0	480	2025-07-07	Deferida	2025-07-07 00:18:04.029271	2025-07-07 00:18:04.035094	BH	f
207	74	1	38	98	2025-06-27	Deferido	2025-07-02 13:58:03.765927	2025-07-07 10:53:33.325976	Festa junina 	f
219	64	3	0	180	2025-05-29	Deferido	2025-07-03 12:52:24.555157	2025-07-07 10:54:23.003383	Decoração festa junina	f
220	21	1	50	110	2025-07-03	Deferido	2025-07-03 22:36:08.355058	2025-07-07 10:54:24.471127	Preparo festa	f
221	45	3	30	210	2025-07-03	Deferido	2025-07-04 00:21:51.606952	2025-07-07 10:54:26.177464	Organização festa julina	f
222	25	3	30	210	2025-07-03	Deferido	2025-07-04 01:40:31.350279	2025-07-07 10:54:27.520559	Confecção decoração festa junina.	f
223	50	4	5	245	2025-07-03	Deferido	2025-07-04 04:24:32.264925	2025-07-07 10:54:44.027415	Enfeitando escola	f
224	69	5	0	300	2025-05-17	Deferido	2025-07-04 16:25:04.159872	2025-07-07 10:54:45.381066	Festa "De quem cuida de mim"	f
225	74	3	17	197	2025-07-03	Deferido	2025-07-04 19:46:14.64653	2025-07-07 10:54:46.629269	Decoração festa junina	f
226	45	3	6	186	2025-07-04	Deferido	2025-07-04 23:19:38.063074	2025-07-07 10:54:48.179182	Organização Festa Julina	f
227	25	2	30	150	2025-07-04	Deferido	2025-07-05 00:19:20.181049	2025-07-07 10:54:49.470882	Confecção decoração festa junina.	f
228	21	2	30	150	2025-07-04	Deferido	2025-07-05 00:36:34.104726	2025-07-07 10:54:51.022248	Preparo festa	f
229	25	11	30	690	2025-07-05	Deferido	2025-07-05 23:04:07.026483	2025-07-07 10:54:53.100982	Festa junina	f
230	25	1	0	60	2025-06-04	Deferido	2025-07-06 11:22:19.059484	2025-07-07 10:54:54.312337	1 hora excedente de reunião HTL.	f
231	45	11	12	672	2025-07-05	Deferido	2025-07-06 14:24:04.021202	2025-07-07 10:54:56.020255	Festa Julina	f
232	50	4	20	260	2025-07-04	Deferido	2025-07-06 15:54:16.844588	2025-07-07 10:55:02.452853	Organização  da escola  para festa	f
233	50	11	11	671	2025-07-04	Indeferido	2025-07-06 15:55:15.367478	2025-07-07 10:55:05.376149	Trabalho na festa 	f
234	50	11	11	671	2025-07-05	Deferido	2025-07-06 15:56:38.909913	2025-07-07 10:55:06.807866	Trabalho na festa 	f
235	19	2	30	150	2025-07-01	Deferido	2025-07-06 19:48:01.684903	2025-07-07 10:55:09.811801	Decoração festa junina 	f
236	19	3	0	180	2025-07-02	Deferido	2025-07-06 19:48:28.297679	2025-07-07 10:55:10.960565	Decoração festa junina 	f
237	19	3	30	210	2025-07-03	Deferido	2025-07-06 19:49:40.368626	2025-07-07 10:55:13.337744	Decoração festa junina 	f
238	19	3	30	210	2025-07-03	Deferido	2025-07-06 19:49:53.600521	2025-07-07 10:55:14.528232	Decoração festa junina 	f
239	19	2	30	150	2025-07-04	Deferido	2025-07-06 19:51:20.314099	2025-07-07 10:55:17.140546	Decoração festa junina 	f
240	19	11	30	690	2025-07-05	Deferido	2025-07-06 19:53:59.415785	2025-07-07 10:55:18.395387	Decoração festa junina / Trabalho	f
243	21	10	40	640	2025-07-05	Deferido	2025-07-07 01:00:58.550431	2025-07-07 10:55:19.837962	Festa	f
244	16	4	0	240	2025-07-05	Deferido	2025-07-07 10:48:25.08234	2025-07-07 10:55:21.649898	Festa junina 	f
245	22	4	0	240	2025-07-05	Deferido	2025-07-07 10:50:02.140288	2025-07-07 10:55:23.258613	Festa Junina	f
246	20	9	20	560	2025-07-05	Deferido	2025-07-07 12:04:38.517677	2025-07-08 17:11:46.530816	Festa Julina	f
247	74	11	14	674	2025-07-05	Deferido	2025-07-07 13:07:40.100193	2025-07-08 17:11:54.972582	Festa junina 	f
248	28	11	0	660	2025-07-05	Deferido	2025-07-07 14:00:01.881622	2025-07-08 17:11:56.344181	Festa julina	f
249	23	5	0	300	2025-05-17	Deferido	2025-07-07 17:26:12.103803	2025-07-08 17:11:57.813841	Dia de Quem Cuida de mim 	f
250	69	12	0	720	2025-07-05	Deferido	2025-07-07 19:09:50.107725	2025-07-08 17:12:00.635457	Festa de Boiadeiro	f
251	64	3	0	180	2025-05-29	Deferido	2025-07-07 19:11:24.951929	2025-07-08 17:12:01.957287	Decoração festa junina	f
252	64	1	56	116	2025-06-04	Deferido	2025-07-07 19:12:25.654633	2025-07-08 17:12:03.677179	Decoração festa junina	f
253	64	1	38	98	2025-06-16	Deferido	2025-07-07 19:18:24.84605	2025-07-08 17:12:04.994824	Decoração festa junina	f
254	64	2	34	154	2025-06-18	Deferido	2025-07-07 19:20:07.5393	2025-07-08 17:12:06.24357	Decoração festa junina	f
255	64	2	0	120	2025-06-24	Deferido	2025-07-07 19:20:47.107553	2025-07-08 17:12:07.387088	Decoração festa junina	f
256	64	3	0	180	2025-06-25	Deferido	2025-07-07 19:21:40.549435	2025-07-08 17:12:09.133929	Decoração festa junina	f
257	64	3	0	180	2025-06-26	Deferido	2025-07-07 19:22:07.770683	2025-07-08 17:12:10.525532	Decoração festa junina	f
258	64	3	7	187	2025-06-27	Deferido	2025-07-07 19:23:31.357519	2025-07-08 17:12:11.760456	Decoração festa junina	f
259	64	2	30	150	2025-06-30	Deferido	2025-07-07 19:24:17.642861	2025-07-08 17:12:12.88155	Decoração festa junina	f
260	64	2	30	150	2025-07-01	Deferido	2025-07-07 19:25:06.059929	2025-07-08 17:12:14.37619	Decoração festa junina	f
261	64	3	10	190	2025-07-02	Deferido	2025-07-07 19:25:48.21729	2025-07-08 17:12:15.518784	Decoração festa junina	f
262	64	3	30	210	2025-07-03	Deferido	2025-07-07 19:26:29.563659	2025-07-08 17:12:17.933152	Decoração festa junina	f
263	64	2	30	150	2025-07-04	Deferido	2025-07-07 19:27:01.346403	2025-07-08 17:12:19.141348	Decoração festa junina	f
264	64	11	38	698	2025-07-05	Deferido	2025-07-07 19:28:53.818794	2025-07-08 17:12:21.14028	festa junina	f
265	68	12	0	720	2025-07-05	Deferido	2025-07-07 22:29:37.533663	2025-07-08 17:12:22.849516	Festa junina 	f
266	49	0	40	40	2025-03-20	Deferido	2025-07-08 14:46:11.916368	2025-07-08 17:12:26.853827	Tive que ficar 	f
267	49	1	0	60	2024-03-28	Indeferido	2025-07-08 14:47:28.914456	2025-07-08 17:12:29.782652	Tive que ficar	f
268	49	1	0	60	2024-03-28	Indeferido	2025-07-08 14:47:52.162146	2025-07-08 17:12:33.600509	Tive que ficar	f
269	49	1	0	60	2025-03-28	Deferido	2025-07-08 14:49:29.995089	2025-07-08 17:12:35.330663	Tive que ficar 	f
270	49	1	0	60	2025-06-23	Deferido	2025-07-08 14:50:06.625942	2025-07-08 17:12:37.029578	Tive que ficar 	f
271	23	4	0	240	2025-07-11	Deferida	2025-07-08 17:24:36.218787	2025-07-08 17:24:36.226367	BH	f
274	18	8	0	480	2025-07-11	Deferida	2025-07-08 20:58:20.858275	2025-07-08 20:58:20.864023	BH	f
275	22	4	0	240	2025-08-04	Deferida	2025-07-08 20:58:35.07657	2025-07-08 20:58:35.080021	BH	f
276	22	4	0	240	2025-08-05	Deferida	2025-07-08 20:58:37.218606	2025-07-08 20:58:37.222103	BH	f
277	22	4	0	240	2025-08-06	Deferida	2025-07-08 20:58:39.843567	2025-07-08 20:58:39.847018	BH	f
278	69	5	0	300	2025-07-30	Deferida	2025-07-08 20:58:43.194852	2025-07-08 20:58:43.198237	BH	f
279	43	4	0	240	2025-07-11	Deferida	2025-07-08 20:58:48.26962	2025-07-08 20:58:48.272831	BH	f
272	72	8	0	480	2025-05-17	Deferido	2025-07-08 20:04:07.001432	2025-07-10 17:07:01.492338	Dia de quem cuida de mim 	f
273	72	4	0	240	2025-07-05	Deferido	2025-07-08 20:05:14.263791	2025-07-10 17:07:07.207733	Festa junina	f
280	44	8	0	480	2025-07-05	Deferido	2025-07-10 14:44:40.183467	2025-07-10 17:07:08.496885	Festa junina	f
281	79	10	14	614	2025-07-05	Deferido	2025-07-10 14:52:22.159306	2025-07-10 17:07:09.463619	Festa Junina	f
282	54	4	0	240	2025-06-23	Deferido	2025-07-10 17:02:06.017187	2025-07-10 17:07:10.188016	Horas da Greve 	f
283	54	6	0	360	2025-07-05	Deferido	2025-07-10 17:02:39.695533	2025-07-10 17:07:11.436121	Festa junina 	f
284	25	8	0	480	2025-07-14	Deferida	2025-07-10 20:12:34.359528	2025-07-10 20:12:34.365004	BH	f
285	25	8	0	480	2025-07-15	Deferida	2025-07-10 20:12:37.326659	2025-07-10 20:12:37.33044	BH	f
286	25	8	0	480	2025-07-16	Deferida	2025-07-10 20:12:43.296738	2025-07-10 20:12:43.300463	BH	f
287	25	8	0	480	2025-07-17	Deferida	2025-07-10 20:12:46.525369	2025-07-10 20:12:46.528659	BH	f
288	25	8	0	480	2025-07-18	Deferida	2025-07-10 20:12:49.302219	2025-07-10 20:12:49.329595	BH	f
289	74	4	0	240	2025-07-14	Deferida	2025-07-10 20:12:55.260859	2025-07-10 20:12:55.264041	BH	f
290	74	4	0	240	2025-07-18	Deferida	2025-07-10 20:12:57.832219	2025-07-10 20:12:57.835972	BH	f
291	19	8	0	480	2025-07-14	Deferida	2025-07-10 20:13:01.512334	2025-07-10 20:13:01.515792	BH	f
292	19	8	0	480	2025-07-15	Deferida	2025-07-10 20:13:07.751801	2025-07-10 20:13:07.755793	BH	f
293	19	8	0	480	2025-07-16	Deferida	2025-07-10 20:13:10.413481	2025-07-10 20:13:10.41679	BH	f
294	19	8	0	480	2025-07-17	Deferida	2025-07-10 20:13:13.096366	2025-07-10 20:13:13.101268	BH	f
295	19	8	0	480	2025-07-18	Deferida	2025-07-10 20:13:15.525406	2025-07-10 20:13:15.528501	BH	f
296	45	8	0	480	2025-07-14	Deferida	2025-07-10 20:13:18.461178	2025-07-10 20:13:18.464389	BH	f
297	45	8	0	480	2025-07-15	Deferida	2025-07-10 20:13:20.998921	2025-07-10 20:13:21.00577	BH	f
298	45	8	0	480	2025-07-16	Deferida	2025-07-10 20:13:23.554602	2025-07-10 20:13:23.558325	BH	f
299	45	8	0	480	2025-07-17	Deferida	2025-07-10 20:13:26.231226	2025-07-10 20:13:26.234612	BH	f
300	45	8	0	480	2025-07-18	Deferida	2025-07-10 20:13:29.223997	2025-07-10 20:13:29.227099	BH	f
301	74	4	0	240	2025-07-15	Deferida	2025-07-10 20:13:34.165096	2025-07-10 20:13:34.168531	BH	f
302	74	4	0	240	2025-07-16	Deferida	2025-07-10 20:13:36.664102	2025-07-10 20:13:36.668038	BH	f
303	74	4	0	240	2025-07-17	Deferida	2025-07-10 20:13:42.24161	2025-07-10 20:13:42.245251	BH	f
304	68	8	0	480	2025-07-15	Deferida	2025-07-10 20:13:44.599639	2025-07-10 20:13:44.602774	BH	f
305	64	8	0	480	2025-07-14	Deferida	2025-07-10 20:13:47.130978	2025-07-10 20:13:47.139327	BH	f
306	64	8	0	480	2025-07-15	Deferida	2025-07-10 20:13:49.796671	2025-07-10 20:13:49.800385	BH	f
307	64	8	0	480	2025-07-16	Deferida	2025-07-10 20:13:52.36881	2025-07-10 20:13:52.37205	BH	f
308	64	8	0	480	2025-07-17	Deferida	2025-07-10 20:13:58.632682	2025-07-10 20:13:58.636113	BH	f
309	64	8	0	480	2025-07-18	Deferida	2025-07-10 20:14:06.528297	2025-07-10 20:14:06.531518	BH	f
310	54	8	0	480	2025-06-27	Deferida	2025-07-10 20:14:09.749004	2025-07-10 20:14:09.754036	BH	f
311	21	4	0	240	2025-07-14	Deferida	2025-07-10 20:14:17.783776	2025-07-10 20:14:17.787883	BH	f
315	45	4	0	240	2025-07-11	Deferida	2025-07-11 16:43:52.511407	2025-07-11 16:43:52.519118	BH	f
316	28	8	0	480	2025-07-17	Deferida	2025-07-11 16:43:57.550979	2025-07-11 16:43:57.554344	BH	f
317	28	8	0	480	2025-07-16	Deferida	2025-07-11 16:43:59.296303	2025-07-11 16:43:59.300954	BH	f
318	28	8	0	480	2025-07-15	Deferida	2025-07-11 16:44:00.93258	2025-07-11 16:44:00.938796	BH	f
312	79	1	0	60	2025-06-23	Deferido	2025-07-11 10:12:17.572322	2025-07-11 16:48:46.296609	Receber TV entrevista EJA	f
313	52	5	0	300	2025-07-01	Deferido	2025-07-11 13:24:03.605308	2025-07-11 16:48:48.002013	Banco Conselho EJA 1 e 2 Trimestres	f
314	52	5	0	300	2025-07-05	Deferido	2025-07-11 13:25:34.244523	2025-07-11 16:48:49.192935	Festa Junina	f
319	28	4	0	240	2025-07-04	Deferido	2025-07-11 16:48:05.532623	2025-07-11 16:48:50.247916	Festa julina	f
320	28	8	0	480	2025-07-14	Deferida	2025-07-11 16:57:28.90321	2025-07-11 16:57:28.906722	BH	f
321	44	8	0	480	2025-07-14	Deferida	2025-07-11 16:57:34.108564	2025-07-11 16:57:34.111707	BH	f
323	50	8	0	480	2025-07-18	Deferida	2025-07-18 18:43:32.57541	2025-07-18 18:43:32.581833	BH	f
324	68	4	0	240	2025-07-18	Deferida	2025-07-18 18:43:41.729303	2025-07-18 18:43:41.73333	BH	f
325	68	8	0	480	2025-07-17	Deferida	2025-07-18 18:43:43.421372	2025-07-18 18:43:43.424909	BH	f
326	20	8	0	480	2025-07-25	Deferida	2025-07-18 18:43:49.909176	2025-07-18 18:43:49.912786	BH	f
327	69	8	0	480	2025-07-29	Deferida	2025-07-18 18:44:01.866827	2025-07-18 18:44:01.870326	BH	f
328	20	8	0	480	2025-07-18	Deferida	2025-07-18 18:44:05.538075	2025-07-18 18:44:05.541403	BH	f
329	1	1	0	60	2025-07-18	Deferido	2025-07-19 20:11:43.769954	2025-07-19 20:11:51.968923	Ponto	f
322	76	5	13	313	2025-06-28	Deferido	2025-07-16 14:10:50.881284	2025-07-19 20:11:56.303925	Trabalho sabado	f
331	15	1	0	60	2025-07-03	Deferido	2025-07-19 22:14:59.879078	2025-07-22 00:19:07.721569	Confecção de enfeite p festa junina	f
330	73	8	0	480	2025-07-05	Deferido	2025-07-19 21:59:05.137063	2025-07-22 00:19:10.812025	Festa junina 	f
332	1	8	0	480	2025-07-22	Deferida	2025-07-22 02:17:48.444795	2025-07-22 02:17:48.745553	BH	f
333	50	0	0	0	2025-07-30	Deferida	2025-07-23 17:51:47.423541	2025-07-23 17:51:47.426602	BH	f
334	18	3	0	180	2025-07-04	Deferido	2025-07-23 20:34:16.901608	2025-07-24 17:33:56.01983	Arrumação para festa junina. 	f
335	18	8	20	500	2025-07-05	Deferido	2025-07-23 20:36:28.642026	2025-07-24 17:34:00.655633	Festa junina 	f
336	1	1	0	60	2025-07-24	Deferido	2025-07-24 17:48:12.20484	2025-07-24 17:48:35.107515	Sistema.	f
337	25	8	0	480	2025-07-25	Deferida	2025-07-24 22:06:42.12271	2025-07-24 22:06:42.130134	BH	f
338	19	8	30	510	2025-07-25	Deferida	2025-07-27 17:06:40.751072	2025-07-27 17:06:40.760593	BH	f
339	47	12	0	720	2025-07-05	Deferido	2025-07-31 18:11:49.989932	2025-08-01 15:23:26.9467	Festa Padin Boiadeiro 	f
340	47	4	0	240	2025-08-01	Deferida	2025-08-01 15:23:34.91352	2025-08-01 15:23:34.91898	BH	f
341	75	8	0	480	2025-07-05	Deferido	2025-08-04 14:53:05.484731	2025-08-05 18:22:02.733143	Festa junina 	f
342	39	6	0	360	2025-07-05	Deferido	2025-08-04 18:40:56.421889	2025-08-05 18:22:03.871432	Festa Junina	f
343	39	1	0	60	2025-07-03	Deferido	2025-08-04 18:42:13.674498	2025-08-05 18:22:04.900887	Retirar prendas em Santos	f
344	39	1	0	60	2025-07-08	Deferido	2025-08-04 18:43:03.382077	2025-08-05 18:22:05.593722	Devolver prendas em Santos	f
345	36	4	54	294	2025-07-05	Deferido	2025-08-05 14:40:34.394788	2025-08-05 18:22:06.277664	Festa Junina horário das 13:17 a 18:11. 	f
346	36	3	3	183	2025-08-07	Deferida	2025-08-05 18:22:16.734035	2025-08-05 18:22:16.739704	BH	f
347	74	4	0	240	2025-08-06	Deferida	2025-08-06 14:15:57.767116	2025-08-06 14:15:57.77393	BH	f
348	59	2	0	120	2025-08-06	Deferido	2025-08-06 15:41:29.585083	2025-08-06 21:39:54.379977	Medico	f
349	1	6	0	360	2025-07-24	Deferido	2025-08-06 21:39:44.780081	2025-08-06 21:39:55.560779	Educador de Apoio	f
350	1	3	0	180	2025-08-06	Deferida	2025-08-06 21:40:21.065479	2025-08-06 21:40:21.069526	BH	f
351	73	4	0	240	2025-08-01	Deferida	2025-08-06 21:40:26.576089	2025-08-06 21:40:26.579751	BH	f
352	25	4	0	240	2025-07-28	Deferida	2025-08-06 21:40:45.062141	2025-08-06 21:40:45.065414	BH	f
353	59	2	0	120	2025-08-06	Deferida	2025-08-06 21:40:57.554661	2025-08-06 21:40:57.5582	BH	f
354	20	5	0	300	2025-07-24	Deferida	2025-08-07 15:52:37.207992	2025-08-07 15:52:37.272347	BH	f
355	21	4	0	240	2025-08-12	Deferida	2025-08-08 18:40:44.757034	2025-08-08 18:40:44.765619	BH	f
356	19	4	0	240	2025-08-08	Deferida	2025-08-08 18:40:48.258988	2025-08-08 18:40:48.264163	BH	f
360	76	5	0	300	2025-08-06	Deferida	2025-08-11 21:35:32.547701	2025-08-11 21:35:32.55716	BH	f
361	45	4	0	240	2025-08-15	Deferida	2025-08-11 21:35:57.264646	2025-08-11 21:35:57.270172	BH	f
362	72	4	0	240	2025-08-29	Deferida	2025-08-11 21:38:21.745709	2025-08-11 21:38:21.750851	BH	f
357	89	8	0	480	2025-07-05	Deferido	2025-08-11 10:42:31.496151	2025-08-12 16:10:33.145981	Festa junina	f
358	89	4	0	240	2025-06-20	Deferido	2025-08-11 10:43:28.996009	2025-08-12 16:10:34.594923	Conselho de escola	f
359	89	3	10	190	2025-07-04	Deferido	2025-08-11 10:44:34.258636	2025-08-12 16:10:35.350156	Organização da festa junina 	f
363	89	8	0	480	2025-08-15	Deferida	2025-08-13 19:03:04.803926	2025-08-13 19:03:04.81126	BH	f
364	19	4	0	240	2025-08-13	Deferida	2025-08-13 19:03:17.094037	2025-08-13 19:03:17.09799	BH	f
365	18	4	0	240	2025-08-07	Deferido	2025-08-14 01:57:36.690488	2025-08-14 13:42:36.855592	Fut pai	f
366	18	4	0	240	2025-08-12	Deferido	2025-08-14 01:58:27.906306	2025-08-14 13:42:37.944865	Cinema- semana da família 	f
367	18	4	0	240	2025-08-22	Deferida	2025-08-15 14:43:36.233763	2025-08-15 14:43:36.241238	BH	f
\.


--
-- Data for Name: esquecimento_ponto; Type: TABLE DATA; Schema: public; Owner: folgas_user
--

COPY public.esquecimento_ponto (id, nome, registro, data_esquecimento, hora_primeira_entrada, hora_primeira_saida, hora_segunda_entrada, hora_segunda_saida, user_id, conferido, motivo) FROM stdin;
16	Tayna da silva siviero 	50495	2025-02-10	07:34	15:50	\N	\N	51	t	\N
17	Tayna da silva siviero 	50495	2025-02-12	06:40	14:41	\N	\N	51	t	\N
18	Tayna da silva siviero 	50495	2025-02-27	06:50	16:51	\N	\N	51	t	\N
19	Tayna da silva siviero 	50495	2025-02-28	06:45	15:00	\N	\N	51	t	\N
15	Danielle Sanches Jaworsky 	46990	2025-03-07	\N	17:30	17:31	\N	54	t	\N
23	Adriana M Queiroz Sambonovich 	47933	2025-03-12	08:00	12:00	\N	\N	79	t	\N
24	Adriana M Queiroz Sambonovich 	47933	2025-03-19	08:00	\N	\N	\N	79	t	\N
22	Tayna da silva siviero 	50495	2025-03-21	06:56	\N	\N	15:00	51	t	\N
20	DAIANA APARECIDA LUIZ SILVA	50526	2025-03-25	07:00	15:00	\N	\N	46	t	\N
26	Rita de Cássia Andrade Alves da Silva 	53168	2025-03-17	15:00	23:00	\N	\N	30	t	\N
27	Radja Brazão 	25375	2025-03-19	07:30	\N	\N	\N	69	t	\N
25	Tayna da silva siviero 	50495	2025-03-27	07:00	15:00	\N	\N	51	t	\N
28	Tayna da silva siviero 	50495	2025-03-27	07:00	15:00	\N	\N	51	t	\N
29	Rita de Cássia Andrade Alves da Silva 	53168	2025-04-02	15:33	23:01	\N	\N	30	t	\N
30	Rita de Cássia Andrade Alves da Silva 	53168	2025-04-08	23:01	\N	\N	\N	30	t	\N
31	Nubia Toledo	51065	2025-04-11	08:00	16:00	\N	\N	12	t	\N
42	Tayna da silva siviero 	50495	2025-04-11	07:00	15:00	\N	\N	51	t	Esquecimento 
36	Amanda F Mondroni Lemes 	17582	2025-04-14	13:30	17:30	\N	\N	23	t	Alfabetiza Juntos 
45	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-04-14	\N	\N	13:30	17:30	19	t	Não registrou.
35	David da Silva Santos	54014	2025-04-23	07:15	\N	\N	\N	65	t	\N
32	Nilson Cruz	43546	2025-04-23	16:00	\N	\N	\N	1	t	\N
63	Renata da Silva Sampaio 	53009	2025-06-02	07:00	\N	\N	\N	82	f	Banco de horas 
33	Nilson Cruz	43546	2025-04-23	\N	\N	\N	16:00	1	t	\N
61	Sandra Cecília de Oliveira 	16970	2025-06-05	\N	12:00	\N	\N	22	f	Não digitei a saída 
34	Nilson Cruz	43546	2025-04-23	16:00	\N	\N	\N	1	t	Ponto com defeito
38	Sheila Gama Costa Rosa	48850	2025-04-24	08:00	12:00	13:30	17:30	28	t	Aluno atrasou 
46	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-04-24	\N	\N	\N	17:30	19	t	Não registrou 
43	Tayna da silva siviero 	50495	2025-04-25	06:00	15:00	\N	\N	51	t	Esquecimento
37	Maria Rosa Rodrigues Dias 	41348	2025-04-25	08:35	\N	\N	\N	50	t	Declaração de horas.
47	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-04-29	\N	\N	13:30	\N	19	t	Esquecimento 
40	Radja Brazão 	25375	2025-04-29	07:30	\N	\N	\N	69	t	Esquecimento
48	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-04-30	\N	\N	13:30	\N	19	t	Esquecimento 
39	Nubia Toledo	51065	2025-05-05	08:00	\N	\N	\N	12	t	Esqueci 
41	Julliana Barbosa Brito Lira	47053	2025-05-06	\N	\N	13:30	\N	21	t	Esquecimento Extra
49	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-05-06	\N	\N	13:30	\N	19	t	Esquecimento 
50	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-05-07	\N	\N	13:30	\N	19	t	Esquecimento 
44	Tayna da silva siviero 	50495	2025-05-08	07:00	15:00	\N	\N	51	t	Esquecimento 
51	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-05-09	\N	\N	13:00	\N	19	t	01h. de HTL
64	Gabrielle Valério Florindo Conti de Moura	51679	2025-06-11	\N	\N	\N	17:40	74	f	\N
65	SILVANDA DIAS DO SANTOS CAETANO	50701	2025-06-10	10:45	06:45	\N	\N	59	f	\N
21	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-03-14	\N	\N	13:30	\N	19	f	\N
66	Vanessa Raquel Rodrigues Borges Amaro 	34221	2025-06-13	\N	15:00	\N	\N	20	f	Seduc Prestação C.
67	Vanessa Raquel Rodrigues Borges Amaro 	34221	2025-06-12	\N	15:00	\N	\N	20	f	Exames e médico.
68	Vanessa Raquel Rodrigues Borges Amaro 	34221	2025-06-17	\N	15:00	\N	\N	20	f	Consulta médica.
75	Eliane Regina de Souza Lima 	42733	2025-06-17	19:00	23:00	\N	\N	47	t	Não reconheceu 
69	Danielle Sanches Jaworsky 	46990	2025-06-18	13:30	\N	\N	\N	54	f	Eu esqueci de bater.
70	Nubia Toledo	51065	2025-06-23	\N	16:00	\N	\N	12	f	Usar 1h10min
71	David da Silva Santos	54014	2025-06-16	06:57	\N	\N	\N	65	f	Esquecimento de pont
59	Tayna da silva siviero 	50495	2025-05-14	07:00	15:04	\N	\N	51	f	Esquecimento 
62	Renata da Silva Sampaio 	53009	2025-05-15	07:00	\N	\N	\N	82	f	Ponto fora do sistem
52	SILVANDA DIAS DO SANTOS CAETANO	50701	2025-05-20	07:00	12:00	\N	15:00	59	f	Usar horas do 17/05
60	Tayna da silva siviero 	50495	2025-05-21	06:33	15:00	\N	\N	51	f	Esquecimento 
53	Danielle Sanches Jaworsky 	46990	2025-05-22	\N	\N	19:00	\N	54	f	Esquecimento. 
55	SILVANDA DIAS DO SANTOS CAETANO	50701	2025-05-23	\N	\N	15:00	\N	59	f	Descontar 1:30 do bh
54	SILVANDA DIAS DO SANTOS CAETANO	50701	2025-05-23	\N	\N	15:00	\N	59	f	Descontar 1:30 do bh
56	Eliane Regina de Souza Lima 	42733	2025-05-29	19:00	\N	\N	\N	47	f	Entrei direto
58	Julliana Barbosa Brito Lira	47053	2025-06-02	\N	12:00	\N	\N	21	f	Exame
57	Janaina Porfirio Santos Michels 	37243	2025-06-02	\N	18:30	\N	\N	73	f	Saí distraída e esqu
72	Vanessa Raquel Rodrigues Borges Amaro 	34221	2025-06-23	06:00	15:00	\N	\N	20	f	esqueci/filha machuc
73	Vanessa Raquel Rodrigues Borges Amaro 	34221	2025-06-24	\N	15:00	\N	\N	20	f	REUNIAO CAE
74	Eliane Regina de Souza Lima 	42733	2025-06-16	19:00	23:00	\N	\N	47	f	não reconheceu 
76	Tayna da silva siviero 	50495	2025-06-16	06:11	15:11	\N	\N	51	f	Esquecimento 
77	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-06-30	\N	\N	13:30	\N	19	f	Esquecimento 
78	ANNE CAROLINE RODRIGUES COELHO	42610	2025-07-01	\N	19:00	\N	\N	32	f	Esquecimento.
79	ANNE CAROLINE RODRIGUES COELHO	42610	2025-06-09	\N	23:01	\N	\N	32	f	Esquecimento.
80	ANNE CAROLINE RODRIGUES COELHO	42610	2025-06-16	\N	23:01	\N	\N	32	f	Esquecimento.
81	ANNE CAROLINE RODRIGUES COELHO	42610	2025-06-18	\N	23:01	\N	\N	32	f	Esquecimento.
82	Gabrielle Valério Florindo Conti de Moura	51679	2025-07-02	08:00	12:00	\N	\N	74	f	Banco de horas 
83	Sidicleia Cristina Ferreira Lima	50062	2025-07-01	\N	15:01	\N	\N	77	f	Bati e não registrou
84	Maria Rosa Rodrigues Dias 	41348	2025-06-23	07:30	13:30	\N	\N	50	f	Usar BH p/ justifica
85	Vanessa Raquel Rodrigues Borges Amaro 	34221	2025-07-05	10:50	\N	\N	\N	20	f	Cheguei trabalhando.
86	TATIANE BEZERRA DA SILVA	24989	2025-07-04	\N	\N	\N	23:00	83	f	Compra festa junina
87	Marcia Garcia Ferreira 	42971	2025-06-16	08:00	12:00	13:30	17:30	44	f	Doação de sangue
88	Nubia Toledo	51065	2025-06-23	\N	16:00	\N	\N	12	f	Médico, usar bh
89	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-07-10	08:00	\N	\N	\N	19	f	Entrada n registada
90	JUREMA BORGES DE SOUZA	44050	2025-07-10	14:30	20:00	\N	\N	52	f	Banco conselho-EJA
91	Eliane Regina de Souza Lima 	42733	2025-07-05	07:30	07:30	\N	\N	47	f	Não registrou entrad
92	Radja Brazão 	25375	2025-07-14	08:00	\N	\N	\N	69	f	Esquecimento 
93	Vanessa Raquel Rodrigues Borges Amaro 	34221	2025-07-10	\N	\N	15:00	\N	20	f	Reunião CAE
94	Nilson Cruz	43546	2025-07-23	08:00	\N	\N	\N	1	f	Esquecimento
96	Nubia Toledo	51065	2025-07-21	\N	16:03	\N	\N	12	f	Médico 
97	Nubia Toledo	51065	2025-07-22	\N	16:05	\N	\N	12	f	Folga concedida dir.
98	Nubia Toledo	51065	2025-07-23	08:30	\N	\N	\N	12	f	Capacitação 
95	Gabrielle Valério Florindo Conti de Moura	51679	2025-07-14	13:30	17:30	\N	\N	74	t	Creche sem ponto reg
99	Adriana Carvalho da Conceição 	27324	2025-08-01	13:29	\N	\N	\N	31	t	Esqueci a saida tard
100	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-07-21	08:00	12:00	12:01	16:00	19	f	Horário direto 
101	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-07-22	08:00	12:00	12:01	16:00	19	f	Horário direto
102	Vanessa Raquel Rodrigues Borges Amaro 	34221	2025-08-11	\N	15:00	\N	\N	20	f	Levar filha no médic
103	MARIA LUIZA GAITOLINI JOAQUIM	27378	2025-08-11	\N	\N	\N	17:30	19	f	Saída não registrada
104	Nubia Toledo	51065	2025-08-18	08:00	16:00	\N	\N	12	f	Esqueci 
\.


--
-- Data for Name: folga; Type: TABLE DATA; Schema: public; Owner: folgas_user
--

COPY public.folga (id, funcionario_id, data, motivo, status) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: folgas_user
--

COPY public."user" (id, nome, registro, email, senha, tipo, banco_horas, status, celular, data_nascimento, tre_total, tre_usufruidas, cpf, rg, data_emissao_rg, orgao_emissor, graduacao, cargo, aceitou_termo, versao_termo) FROM stdin;
69	Radja Brazão 	25375	radjabrazao@gmail.com	pbkdf2:sha256:1000000$ykhP7qhMArf0XubI$99636351b8c546a8236240a0f250d9b756c4fe472a8b5ee2bd93ca4342e82b81	user	240	aprovado	(13) 97415-3738	1983-09-09	0	0	300.926.378-33	32.682.116-8	2013-12-26	SSP-SP 	Licenciatura	Agente Administrativo	t	2025-07-25
30	Rita de Cássia Andrade Alves da Silva 	53168	petchenatidilicia@gmail.com	pbkdf2:sha256:1000000$pxJpamXknETmob5N$de6c5288faaac31b0bb6a0d5ea36faae62d3a95442ed9cf12b3699cbde65cd3e	user	1890	aprovado	(13) 98836-3536	1984-05-19	0	0	348.196.898-19	44.332.045-7	\N	\N	\N	Servente	f	\N
27	Vanusa de Farias Vidal Souza	6441	vanusavidal18@gmail.com	pbkdf2:sha256:1000000$xr2kC29ra3KIYROd$30d11bac207f6b6ec1d079da0af00f7649b92c4b763bb529be0a9929dbdd7ed5	user	0	aprovado	(13) 98213-3276	1970-04-07	2	0	097.809.268-60	23.321.979-1	\N	\N	\N	Professor I	f	\N
37	Rosbergio paraibano da costa 	22370	rosbergiocosta@hotmail.com	pbkdf2:sha256:1000000$4haGg4Bd29d2SiqC$f7505407a4b205670efcc0590f045204f28a5f9de94da5c2610f7c91042b5037	user	0	aprovado	(13) 98187-7615	1983-05-15	0	0	324.197.308-52	41.629.105-3	\N	\N	\N	Trabalhador	f	\N
63	Conceição Aparecida Medici Modesto 	29612	Conceicaomedici@gmail.com	scrypt:32768:8:1$4yzKfAhxsxwaTQFZ$980bf8d7e94c7da887dc1e2d46aaccc588d5ac39918cd0d02c7758092aff580dbcdaccc81b018dad91c3d3520a2529e818dab2f1e374bd866ff0c072ef33e980	user	0	aprovado	(13) 98151-3101	2025-03-08	15	0	103.992.478-66	22.344.163-6	\N	São Paulo 	Licenciatura	Servente II	f	\N
110	Administrador2	000000	administrador@gmail.com	pbkdf2:sha256:1000000$9rC7HjkHUj1euOh6$dc3c9ddb1d35e4326d86b45bdfea6e8146d6caa22d78b65f5914419ffbf3d618	funcionario	0	rejeitado	(13) 99163-2819	1994-08-20	0	0	123.125.612-42	23.175.923-4	\N	\N	\N	Agente Administrativo	f	\N
31	Adriana Carvalho da Conceição 	27324	aconceicao@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$4jFyPnyfb5hS8trB$fffe370c1e1ff21c0954d4062264e3c049c3a0f881fc6056dd2b9047a9679fa4	user	602	aprovado	(13) 99791-3058	1977-08-19	6	0	259.891.328-08	29.396.536-5	\N	None	Pós Graduação Latu Sensu	Professor I	t	2025-07-25
43	Fernanda Gibertoni Sanches 	19395	fsanches@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$10bsHcdCFlNrpmin$7447688c34c56989bf69331302ca27b375a4629fe898f5776708ae98f4d8c0db	user	0	aprovado	(13) 98867-5795	1973-05-22	10	0	246.108.258-80	22.839.446-6	\N	None	\N	Professor I	t	2025-07-25
39	Fabiana Gonçalves de Matos Reis	34928	fabiana.goncalves.matos@gmail.com	pbkdf2:sha256:1000000$CP5zsqpQl2At6yNA$9263f720693ca3fbe794511ce4550d0658c2ef8dae5eb5327937306142c1a87a	user	480	aprovado	(13) 99191-0793	1977-04-06	5	0	275.372.728-75	28.600.717-4	2024-07-29	SSP	Pós Graduação Latu Sensu	Professor I	t	2025-07-25
36	Allan Rovert Leite 	42382	allanrovert@yahoo.com.br	pbkdf2:sha256:1000000$JzfJj6LUutCk4ogZ$4d3bd6e027b1615eb470cafbcd0e2f9617a57e3dd41cd2f5e2718ccc74f6960d	user	111	aprovado	(13) 99179-0084	1988-04-03	4	1	376.352.028-71	32.945.256-3	\N	Ssp	Pós Graduação Latu Sensu	Professor IV	t	2025-07-25
28	Sheila Gama Costa Rosa	48850	sheilaletras13@outlook.com	pbkdf2:sha256:1000000$YwjRGtsICfGwfyqC$1c3c73abd3de377a51a506f7bb4d318a24cdbc1955ae281a64be794cd7cb1688	user	16	aprovado	(13) 99171-2244	1976-06-28	9	0	980.099.075-53	66.797.954-2	2020-03-13	São/AP	Pós Graduação Latu Sensu	Agente Administrativo	t	2025-07-25
24	Alexandra Festa	50698	alexandrafesta.portal@gmail.com	pbkdf2:sha256:1000000$d3tR2SpRDkLvqlFE$1b7252f223089edae65969e246196d6629489b67f51811bd59cc7b923e09bace	user	0	aprovado	\N	\N	0	0	\N	\N	\N	\N	\N	\N	f	\N
35	Carla Roberta Cabral dos Santos costa 	34104	carla.cabral0404@gmail.com	pbkdf2:sha256:1000000$5zTlyuXALYZCXPyH$9a52b6a4c3d2dc74a09f4da91a771e45f3bc529f487cd719bb1880f20a46d651	user	0	aprovado	\N	1987-04-04	0	0	349.154.668-09	41.202.290-4	\N	None	\N	\N	f	\N
38	Bruna Da Silva Mattos	53296	brunam1703@gmail.com	scrypt:32768:8:1$AbeVn7Trqxwt8IQi$57b65b0851787d2349d681d14e9099d3a157515e00c208924743e25f58956e630f172a4addf1df295658d7442359001ac5d514d616a852c52d59711df7bffddd	user	0	aprovado	\N	\N	0	0	\N	\N	\N	\N	\N	\N	f	\N
34	TIAGO HUMBERTO CABRIL BATISTA	41581	tiagohumbertobatista@gmail.com	pbkdf2:sha256:1000000$GGDkwJmd1MeuwXCB$e7976ea1ae2b37e6711916bfe96a6f9460498b6654021f31b912bd4d557a955c	user	0	aprovado	\N	\N	0	0	\N	\N	\N	\N	\N	\N	f	\N
40	MARCOS JOSÉ DE QUEIROZ	18541	macos-jose@hotmail.com	pbkdf2:sha256:1000000$K8cS5YeoDDKf0Ngu$41f8e4a1759af440495cf106026d6aec0c8b78f191b6268e6cdcf1a4833d312c	user	0	aprovado	\N	\N	0	0	\N	\N	\N	\N	\N	\N	f	\N
42	Escola José Padin	9999999999	em.padin@praiagrande.sp.gov.br	pbkdf2:sha256:1000000$5iUExWyRdNNpstIf$f77eadb2ee009be63317e4419b174a16270b2ce6e9bb31d829d77052c244ee0f	administrador	0	aprovado	\N	\N	0	0	\N	\N	\N	\N	\N	\N	f	\N
53	CARLOS MAGNO FREIRE ROSEMBERG 	41018	crosemberg@educacao.sp.gov.br	pbkdf2:sha256:1000000$uTz9dSPsEHZm1fXO$e20a6860579adaee7823e48153aad5e343039464e89b0028639d339606b58c7d	user	0	aprovado	(13) 13982-2175	1960-03-29	0	0	034.884.858-70	11.847.065-6	\N	NoneSSP	Pós Graduação Latu Sensu	Professor IV	t	2025-07-25
112	Laudilene V. S. Pereira 	37136	laudilene_santos@hotmail.com	pbkdf2:sha256:1000000$iWphylHPbWgM7W0z$c2ad7726c997d1ab955765dc64547a732949bca07cf1d454d8ce33c737738d1c	funcionario	0	aprovado	(13) 99116-6262	1984-11-01	0	0	048.385.414-06	53.342.365-_	\N	\N	\N	Professor III	t	2025-07-25
65	David da Silva Santos	54014	david02011999_@hotmail.com	scrypt:32768:8:1$y5JHPwhcu3hV8oGz$3a05051dc29b96411aca5d4af4f34877c0d730aa237ca682752df89738c72e8548f8c98932e4606bd7aa6db98018cb6e6710565c6309eac9fb047ee81239272d	user	0	aprovado	(13) 99698-9869	1999-01-02	0	0	238.759.578-57	55.916.982-6	2017-07-07	SSP	Técnico	Inspetor de Aluno	t	2025-07-25
23	Amanda F Mondroni Lemes 	17582	alemes@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$6J0FzEsZMzp3bpVs$1e9b5f666c2e2d998f7562157c5891e74cefaf2b0520e18821f7923bface6dbf	user	60	aprovado	(13) 99177-1995	1978-12-01	12	0	277.873.438-42	30.070.127-5	2010-07-13	SSP	Pós Graduação Latu Sensu	Professor I	t	2025-07-25
111	Nilson Cruz	0000000	administrador2@gmail.com	pbkdf2:sha256:1000000$y0AuwOHyjUOEnneu$13f0d975351bbc7ee6ed6781740ac6fdc26c7cf5250b6a7f57f943a45acd827d	funcionario	0	aprovado	(13) 99163-2819	1994-08-20	0	0	838.383.838-83	83.883.888-3	\N	\N	\N	Agente Administrativo	f	\N
1	Nilson Cruz	43546	nilcr94@gmail.com	scrypt:32768:8:1$mrbNycEWWlnZGp0d$10236a334a10a3f863bcd0fe09b067c937d4db0d8ed43fba4cc1e7e161994fd7008fbecd36f3905f8d578d6e4560a811c3dd9d054976f0ff43b9f5a2ba16e984	administrador	270	\N	(13) 99163-2819	1994-08-20	0	0	433.502.318-96	53.175.923-4	2009-08-27	SSP/SP	Pós Graduação Latu Sensu	Agente Administrativo	t	2025-07-25
58	Leidiane do Nascimento Costa Almeida 	55083	leidiane_virtual@hotmail.com	pbkdf2:sha256:1000000$8WoYqQrA7OsHBgxe$93f9bab058989ed1d9802a6807ccdc315879fe12ce8cf5442df3e984b059489a	user	0	aprovado	(13) 99681-6639	1985-11-15	1	0	350.206.468-73	42.724.682-9	\N	\N	\N	Professor III	t	2025-07-25
47	Eliane Regina de Souza Lima 	42733	ereglima@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$ZG9QAbxodvYMXQdj$a295fc9d9d27ca220b675e828ee4a96b60aa32a7ac927b10ae279e901950b149	user	480	aprovado	(13) 99788-6119	1971-06-27	5	0	109.178.478-73	21.435.318-7	\N	None	Mestrado	Professor Adjunto	t	2025-07-25
64	Cristina Gerlach Cezario 	40019	cristinagerlach667@gmail.com	pbkdf2:sha256:1000000$WKWarw4H90B0nL1K$1efc0d21f618a27fa9ea9a242c0858666018541b3f46951b1f0facd6ffe7a590	user	2210	aprovado	(13) 98834-2864	1975-09-25	0	0	252.736.798-42	27.107.442-5	\N	\N	\N	Educador de Desenvolvimento Infantil	f	\N
57	Ana Carolina dos Santos Pereira 	33645	annacarolinapereira17@gmail.com	pbkdf2:sha256:1000000$H0vC0OxWOwroXsgB$dee3190b00e12de705a659cfc5eaafae26020eedd17281edf15fe96c575650b9	user	0	aprovado	\N	\N	0	0	\N	\N	\N	\N	\N	\N	f	\N
56	Raphael Guedes Luiz	46340	profraphaelguedes@gmail.com	pbkdf2:sha256:1000000$Az5Ryh5Cn0nNRYth$bd89ca1ebaf4f43ab1aebf312e05271cdf5c6964f76b7a0f24274900357975b2	user	0	aprovado	(13) 98223-7970	1982-08-14	0	0	317.611.218-12	47.010.898-8	\N	\N	\N	Professor IV	f	\N
62	Guilherme Oliveira de França 	51443	gui-o-f@hotmail.com	pbkdf2:sha256:1000000$ONheh8t5RRv2Bd04$621a48984b80f871366252a46b7643540f60bdffa05238f3aac98ecca5df20aa	user	1815	aprovado	(13) 99187-8609	1997-04-08	0	0	463.057.308-90	45.767.954-9	\N	\N	\N	Atendente de Educação I	f	\N
79	Adriana M Queiroz Sambonovich 	47933	drikasambo@gmail.com	scrypt:32768:8:1$nZcroe6mWCcXND8B$e0c628957a4f2effde2aed6751b5b169f7b495ce7c5451c0964551d2a9ffde2de23a79b6527140409ce55e065c20dcff04de41bb6e23f335473c89761d01271f	user	1214	aprovado	(19) 99904-3435	1973-03-18	0	0	175.701.598-10	25.355.487-1	2025-03-26	sSP	Pós Graduação Latu Sensu	Professor Adjunto	t	2025-07-25
75	Carlos Alvarez de Souza 	37231	csouzaalvarez@gmail.com	pbkdf2:sha256:1000000$hVxSkzGPWD2JPxMU$f4e71a0e077d8f5466dad4ba63a71e4da54bdf72df1890bfb14cbb8323a2a57c	user	480	aprovado	(13) 99148-6656	2025-11-02	0	0	252.458.348-12	28.039.305-2	\N	None	Pós Graduação Latu Sensu	Professor III	t	2025-07-25
67	Renan dos Santos Montanheri 	47308	renanmontanheri@hotmail.com	pbkdf2:sha256:1000000$5Y363HB1eY93QIp0$86b88a8712a338d5e90f23d70f6a9c55e317a3d6feb4b4add14534807692b2ca	user	0	aprovado	(13) 99773-5839	1990-03-15	0	0	392.909.698-65	46.201.394-7	2023-03-23	Ssp	Técnico	\N	f	\N
88	Conta Teste	777222	contateste@gmail.com	pbkdf2:sha256:1000000$jht4OmHpsjd0OewI$72aa85c6b86c85c054ca8f5900902736359985729551fed369bfb663786f2920	funcionario	0	aprovado	(13) 99163-2819	1994-08-20	0	0	121.371.698-51	15.738.938-8	\N	\N	\N	Atendente de Educação II	f	\N
107	Administrador Cruz	00000	nilcruzlneto@gmail.com	pbkdf2:sha256:1000000$d2wUwx0hi2LHESLC$f6f3c7559e4abdae9cdc245a593c51cd31ca6913c992093de7f3f86ba03a43b0	funcionario	0	aprovado	(13) 99163-2819	1994-08-20	0	0	562.861.270-70	27.284.532-2	1994-08-20	SSP/SP	Pós Graduação Latu Sensu	Agente Administrativo	t	2025-07-25
26	Caroline Sati Muller	32536	poentecarol@gmail.com	scrypt:32768:8:1$KPP3TxuZlI5ScMME$8d4a0132bff0d1322cb0d0928accfe65fc4658383e951c2d54600ceca347bccf608b9fe76c082b58c36fdbf370aff8b5cbbbcb0f585ca707806e25e95a7725a1	user	480	aprovado	(13) 99740-4540	1984-10-07	17	0	329.892.628-06	33.826.554-5	\N	None	Mestrado	Professor I	t	2025-07-25
90	Conta Teste Univesp	090909	contatesteunivesp@gmail.com	pbkdf2:sha256:1000000$uZhDqXb6udtnkVX2$8657a1fdf426b6f541c43e030a41e4903819961b9bd553b9227a756dfab9eb69	funcionario	0	aprovado	(13) 99912-4543	1994-08-20	0	0	122.344.533-45	54.124.564-4	\N	\N	\N	Agente Administrativo	f	\N
89	Bruna Michelle Barreto 	28027	bbarreto@educacaopg.sp.gov.br	scrypt:32768:8:1$CglyVWOKVkoxtdcO$8345bfdba9a4ffb67609ade7622fd79e40d84f9a74d4c78e51124688b03977dbdcfaef51f8884efff6ec7f4289626f172dedf8c1fe3de1c7890d2b1f7672686c	funcionario	730	aprovado	(13) 99796-1271	1981-11-12	2	0	214.377.638-12	29.932.449-7	\N	\N	\N	Professor I	t	2025-07-25
60	Marcos José de Queiroz	18531	marcos.jose.queiroz.1973@gmail.com	scrypt:32768:8:1$SIdAFm3OPu6hrbn3$e24838c4225a121ff7779116f5ff64199e5c6375de71d098f89eeb7cea9238d25de5fb181a8a866cb1db08cac2e82f6e82d3d367c956e3fd8a34e171a0f4ad49	user	0	aprovado	(13) 98855-4727	1973-05-26	0	0	197.656.128-00	26.216.026-2	2013-01-05	SSP	Tecnólogo	Agente Administrativo	t	2025-07-25
3	Emi Mariane Muller 	39531	emuller@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$P980TQMp12UokXzP$a4f79bf7db460f904c4056011e4f0c2fd8c24f5c6ebac5c0a6267ef28497f97c	user	0	aprovado	(13) 98814-4246	1981-03-20	8	0	298.539.058-33	33.382.655-3	\N	\N	\N	Professor Adjunto	t	2025-07-25
92	EMANUELE PATRICIA DE ANDRADE OLIVEIRA ACAYABA 	42618	professoraemanueleoliveira@gmail.com	pbkdf2:sha256:1000000$v9Shhqqo4brekkG7$71aaff0799a433d90f887ac51434d556dd159e29659298cab321bbcbde0e7989	funcionario	0	aprovado	(13) 99753-4606	1982-02-23	0	0	306.966.148-39	44.424.571-6	\N	\N	\N	Professor Adjunto	t	2025-07-25
18	ANDRESSA LINA MOREIRA DIAS	19398	aldias@educacaopg.sp.gov.br	scrypt:32768:8:1$TsXRzvYrc6D1797V$7ffe31cf65e7546c4d93f2dfcf10bf5befe23b28981a76389a4f2583d5fcb848de4dd5c198a8564eaa0298a3a627f565aaf195debd53623abeae78281c88fcc7	user	1050	aprovado	(13) 97421-3922	1980-06-16	0	0	286.411.578-67	27.992.449-5	2019-07-24	SP	Pós Graduação Latu Sensu	Professor I	t	2025-07-25
2	Cleide de Pontes Oliveira Teixeira 	27394	cleideppot@hotmail.com	pbkdf2:sha256:1000000$zpxr4CaHXSXsGIDU$b366438cf562761ab3d0459376d33a7100c28157697a3b25b48c9986553b4985	user	480	\N	(13) 99739-6303	1973-02-26	10	0	128.268.528-76	22.841.290-0	2015-09-21	SSP-SP	Pós Graduação Latu Sensu	Professor I	t	2025-07-25
70	Márcia Regina Motta	40683	monicasempre@hotmail.com	pbkdf2:sha256:1000000$JlJYfmDwOq9oQY7w$8dde9245cbd026236380af8bd85eb9631575fbf8ccb1aa65ece705708646aaec	user	0	aprovado	(13) 99641-8982	1963-02-20	0	0	044.410.358-96	15.736.246-2	\N	None	Técnico	Servente I	t	2025-07-25
93	Ana Paula Fonseca de Jesus Cavalheiro 	42609	acavalheiro@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$eZzDr02T3SxBINEf$ecaa803daf722bd8db2c3d9f5b603858624ba384328a4b5ab6caec092510f317	funcionario	0	aprovado	(13) 99128-1484	1980-12-23	1	1	218.507.418-08	33.824.379-3	\N	\N	\N	Professor Adjunto	t	2025-07-25
104	Luciana Pedrosa Rodrigues Barbosa 	40748	Lpedrodrigues@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$9pGcqluKJKdUc8Ky$afe6e1984e9b5fa60491d8911a565b28c888f84fdf7d75d210784bd37224a6e4	funcionario	0	aprovado	(13) 99750-5797	1977-08-22	0	0	265.420.958-02	27.843.267-0	\N	\N	\N	Professor III	f	\N
103	Jéssica dos Anjos Almeida	36235	jessicaanjos232@gmail.com	pbkdf2:sha256:1000000$T8QmdM1jE9a5YIwi$c7c97d226ee61c3df99bba1ec242c13cbc6eb8c75b70403fd231e863fc2f7f18	funcionario	0	aprovado	(13) 99101-6825	1984-02-25	0	0	357.839.458-03	23.597.649-0	\N	\N	\N	Servente	f	\N
78	Gleide de Macedo Borges	43099	gborges@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$V5asVZQB2TpBUjyy$17d5fcff8f93d79d367df7abe8e15205d6020dc4a38fa023b6c570d524bed889	user	0	aprovado	(13) 99178-8959	1982-11-26	0	0	302.833.388-06	34.712.414-8	\N	\N	\N	Professor IV	f	\N
14	Maria Cristina Clemente e Silva 	32470	clementemariacristina14@gmail.com	pbkdf2:sha256:1000000$4WV8UfqSXgXJg9A6$786c9fec9fec67a1dfee1e3dc32568618a6e792f35ad44a7a65e5be9c0842e7e	user	0	aprovado	\N	\N	12	0	\N	\N	\N	\N	\N	\N	f	\N
22	Sandra Cecília de Oliveira 	16970	sandraprof76@gmail.com	pbkdf2:sha256:1000000$vnQCtcZYPRHlRiLO$16686281757559c074651f0c383fa286b228c3d5cba56d665285b089e3a80acc	user	0	aprovado	(13) 99610-3157	1976-06-26	0	0	255.072.608-18	25.556.502-1	2012-08-30	SSP/SP	Pós Graduação Latu Sensu	Professor I	f	\N
61	ANDREIA MARTINS CAETANO PRADO	49887	deiamfaria@gmail.com	pbkdf2:sha256:1000000$tiSgVc5cMoeuUHZO$d9775339d4f09345645e1f643541438e61028f19f1577af5bdab1776059bc146	user	0	aprovado	\N	\N	0	0	\N	\N	\N	\N	\N	\N	f	\N
33	Juscelia Florio da Silva Ferreira 	21155	floriodasilvaferreirajuscelia@gmail.com	pbkdf2:sha256:1000000$JiyWPLFk3qjc1bne$e5207e1f3e723d15a2261dab83d2b90a5adc88c97b47c74faea596bae325a102	user	0	aprovado	\N	\N	0	0	\N	\N	\N	\N	\N	\N	f	\N
48	ERIKA FERNANDES INVERNIZZI	43591	erikafernandes253@gmail.com	pbkdf2:sha256:1000000$nXcfbAXn6ArgKuLB$7720595cebee7d5d38139a310a4fbba99b9040dbc8a439fadf26e31b6c9484d3	user	0	aprovado	(13) 99185-9911	1985-04-15	0	0	334.562.738-86	42.895.621-_	\N	Ssp	\N	Servente	t	2025-07-25
21	Julliana Barbosa Brito Lira	47053	jullianabrito2@gmail.com	scrypt:32768:8:1$9HAhWw0Kp7lwJxyo$7046a71121c090466f4ca5f4088b4a6a6be54b81d8a161b6116af4c5e420d80fb07f3d608d686704cf6f381f853c9131d78d8fa4351779f66ee4dd7c99925e62	user	1080	aprovado	(13) 97424-3624	1986-09-08	0	0	326.596.998-36	40.793.293-8	2020-12-30	SSP/SP	Técnico	Atendente de Educação I	t	2025-07-25
54	Danielle Sanches Jaworsky 	46990	danielle.sanches.js@gmail.com	pbkdf2:sha256:1000000$yoQPcsHJuFD8WFu9$0e9e0943b32b6edaac9b14c181d625525ffbbdf0f4ba6fa5133b8adf814a9849	user	120	aprovado	(13) 99159-4982	1980-01-25	0	0	212.978.478-06	32.677.892-5	2024-01-19	SSP/SP	\N	Educador de Desenvolvimento Infanto Juvenil	t	2025-07-25
52	JUREMA BORGES DE SOUZA	44050	jbsouza@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$CD4lW9iEybvFWIf5$01fdea721637fce942063324a785fa7a91e19fc65f1b08f011740ccad3f76c38	user	600	aprovado	(13) 99155-9703	1980-11-15	0	0	291.629.158-00	35.146.397-2	\N	SSP SP	Pós Graduação Latu Sensu	Professor IV	t	2025-07-25
68	Alice de Oliveira Bialtas 	47559	bialtasalice@gmail.com	pbkdf2:sha256:1000000$BnsJM3Jx3YqhsCbH$be35da1551687ff4aa7a9805c336784a103a27efe1ce8a55b7fa253d8ba2ff9f	user	120	aprovado	(13) 98852-2758	1969-03-30	0	0	254.159.468-29	17.679.176-_	2020-02-04	São Paulo 	Pós Graduação Latu Sensu	Educador de Desenvolvimento Infanto Juvenil	f	\N
32	ANNE CAROLINE RODRIGUES COELHO	42610	annecaroline_33@hotmail.com	scrypt:32768:8:1$MwLGNIIz8vftUD3E$0b010cf934a479b805362352d76b624ea0bc803b509e7dd66299b1d9bdaeae9f2272d5c95ff3a3adccb281fa023e01af6b6d5f3a83e4d06a0a8752ca19149019	user	0	aprovado	(13) 98132-8543	1985-05-04	0	0	343.955.938-60	41.017.699-0	2023-06-12	SSP-SP 	\N	Servente	t	2025-07-25
76	Elder souza nunes	52794	elderdaise@hotmail.com	pbkdf2:sha256:1000000$M9eKqZLCzye9Gcah$ee551554615fc404411e5b8112d90921a37823772ac5c723ef746c3b11cf0b42	user	13	aprovado	(13) 99790-9564	1987-08-03	0	1	356.239.438-10	40.519.401-8	\N	SSP	\N	Trabalhador	t	2025-07-25
16	Regina Tschege Ferrari 	27190	rferrari@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$C4yeKAeCVtONvgNz$43607405ff4e2ea368ab89d4680e35a2b4d876f401b0982cf329211cefa2213f	user	240	aprovado	(13) 98832-4705	1958-06-11	13	1	263.334.478-03	8.708.787-X	2017-07-21	SSP -SP	Pós Graduação Latu Sensu	Professor I	t	2025-07-25
46	DAIANA APARECIDA LUIZ SILVA	50526	daianaluiz466@gmail.com	pbkdf2:sha256:1000000$0dfExMyzQnvOjC4K$c590f199990faaffcf7bdf4d0353bd047877e098545322b6cf73f6b949e77ee5	user	1300	aprovado	(13) 98126-1006	1986-09-04	0	0	339.212.038-30	25.232.815-2	\N	\N	\N	Servente	t	2025-07-25
73	Janaina Porfirio Santos Michels 	37243	janamichels@gmail.com	scrypt:32768:8:1$SWNhS69XEJgrEn45$6ee256a83f12571ba431c4a4af8e3e815cf26868af3c5e54117ec8d610cf185bdce71882c7e58e6a1fca2b5cbe47e98d5f2a6d079e30c131be3691c6304a4707	user	360	aprovado	(13) 98226-7298	1976-01-13	0	0	250.526.888-65	26.552.735-1	1994-08-30	SSPSP	Pós Graduação Latu Sensu	Professor Adjunto	t	2025-07-25
55	Juliana Salim 	31797	JulianaSalimpg@hotmail.com	scrypt:32768:8:1$5ua0SBUGKBIRSqyl$506a24a8422d2f6fd22e412dda0306c09018056fa88ad59455bc6a67c2e69f02f5382e3fac1f3987bd7384f9697ec9a88f996997e39bcaf3c37f82ffc3ae1459	user	0	aprovado	(13) 98110-3477	1976-05-05	0	0	295.393.048-57	29.932.920-3	2023-03-30	Ssp-sp	Licenciatura	Inspetor de Aluno	t	2025-07-25
44	Marcia Garcia Ferreira 	42971	marciadlira@hotmail.com	pbkdf2:sha256:1000000$WG33UqaVrL95mmyn$5258cfb379df66a7ee88f5c5e8e68edc77c4cc29b0c6e1582776d8efbcfa3f09	user	0	aprovado	(13) 99718-4950	1988-11-07	0	0	230.513.268-95	44.846.397-0	\N	None	Pós Graduação Latu Sensu	Atendente de Educação II	t	2025-07-25
41	Ildelena Cavalcante Lima 	40262	ildelena_cavalcante@hotmail.com	scrypt:32768:8:1$Vy4fqrCpOAsq5CTj$256ab52419de767e82fc3c2c33a605fc3e19b5eb365ac97da7d6f934c901c06baef42b04292d234c8584b807a89a54ba4726c6e9defeb30343e15735513f7597	user	0	aprovado	(13) 13988-5159	1984-04-28	0	0	002.262.503-85	57.013.394-4	\N	SSP	\N	Inspetor de Aluno	t	2025-07-25
15	Eliana Maria Vicentin LIsboa	32522	elisboa@educacaopg.sp.gov.br	pbkdf2:sha256:1000000$CbtlEDu8zhnetcav$248f571d86121884beedfdd8e6bba49581a85c87b21ee9b3dac5ada623989d8b	user	60	aprovado	(13) 99739-0098	1964-02-15	1	0	060.668.158-22	13.654.836-2	2013-02-07	SSP	Pós Graduação Latu Sensu	Professor I	t	2025-07-25
72	SILVIA CRISTINA MEYER AZAMBUJA	14880	silviacmazambuja@gmail.com	scrypt:32768:8:1$RKEI7gZD2uqfYIEQ$adec5168e0101cf61f37f93b98ad196e7c73090d637754e9ca215dd273f790038ee06f83a1960af723dfbfd88d9ad23b2b7d119d02c5847ebd24ce68bc5577d7	user	480	aprovado	(13) 99754-9129	1976-06-21	2	0	253.290.008-31	19.192.184-1	\N	\N	\N	Professor I	t	2025-07-25
71	Rafael Fernando da Silva	46034	brsrafa@gmail.com	pbkdf2:sha256:1000000$IV03rUgeDvrWZlia$3436aca6899bea5dca5eab72ecb0396fe4c6b828780d062b14a904c49dfb34b8	user	175	aprovado	(13) 98835-3107	1987-09-16	0	0	349.317.458-65	29.230.205-8	\N	SSPSP	Tecnólogo	Agente Administrativo	f	\N
91	Vinícius Vieira	47737	vsvieira93@gmail.com	pbkdf2:sha256:1000000$GKZuhVYMstdIQ8P3$809a3c52e8e5b950c3cc4358dbea7f922b695424e15ad6986106cd34017dda87	administrador	0	aprovado	(13) 99643-3025	1993-01-12	0	0	326.906.678-35	48.786.789-0	\N	None	\N	Agente Administrativo	f	\N
29	Thais de Carvalho Pimentel 	47817	tutyka2011@gmail.com	pbkdf2:sha256:1000000$QAyNXqm3YChpuH2O$aba03c15c01111c5adedb71701fed0476c8e1b3033ee4018dafe13e31343d2d0	user	60	aprovado	(13) 99183-8403	1984-04-24	0	0	326.256.068-51	32.917.610-9	\N	None	Pós Graduação Latu Sensu	Agente Administrativo	f	\N
82	Renata da Silva Sampaio 	53009	resampaio83@gmail.com	scrypt:32768:8:1$gC0pJMtxRHW7QI3b$7e278f54b63ba8cabf682be7d5dca4d78c24147b9fd3770a8a5ae9cea2c892d559070929e15f82aecc859bf24f84b76cd14088950ed7682e915cb5a310f279e1	user	0	aprovado	(13) 99150-7744	1983-02-23	0	0	320.909.238-90	43.917.697-9	\N	\N	\N	Servente II	t	2025-07-25
51	Tayna da silva siviero 	50495	tayna1309@hotmail.com	pbkdf2:sha256:1000000$obw4NHMq7Mv64oLv$8e00781408217e6ab7dba9c26e6e21b16922a750c1e300abdda6843515b1a075	user	1206	aprovado	(13) 98878-2028	1995-09-13	0	0	445.975.058-90	43.270.649-5	\N	None	\N	Agente Administrativo	t	2025-07-25
19	MARIA LUIZA GAITOLINI JOAQUIM	27378	lugaitolini@hotmail.com	scrypt:32768:8:1$KozF3f8QCvRP0aez$9eb0ad7a4a6f406186b616351e61128c575f9b2607f0ec97182f31a3dc6c509bd75165802063b7a6794977dca2ad9e3690e8b3a1f2d75637fd97dd34e1c29434	user	90	aprovado	(13) 98855-5585	1996-10-17	13	2	062.209.798-93	18.274.442-5	2019-09-24	SSP	Pós Graduação Latu Sensu	Educador de Desenvolvimento Infanto Juvenil	t	2025-07-25
108	Beatriz Tarosso Pedroso	55261	biiazinha12233@gmail.com	pbkdf2:sha256:1000000$hnocI8jMuxBOdgf1$1d9df5614a021b2de98bf3a0ba8ebb99d6634a0919f05615ec0679ade4671ad6	funcionario	0	aprovado	(13) 99621-2788	1996-12-26	0	0	349.631.368-48	48.426.912-4	\N	\N	\N	Servente I	f	\N
66	Renata da Conceição Nascimento Galvão 	53427	renata.kade@hotmail.com	scrypt:32768:8:1$Q6J8GH7I9cRkypW7$fd779d15b3d856ae823e69ced9b2e0c73909fc7d8229f77f1b1c46ef7834083bccee37a28fd99329f7882bbc00cebd9526904b6a908730109d872bd9a21f1f7d	user	260	aprovado	(13) 99718-5653	1981-11-17	0	0	301.819.558-22	34.448.933-4	\N	None	\N	Servente II	t	2025-07-25
49	Maria Claudia Guimarães de Freitas 	18780	andrepraiagrande@hotmail.com	scrypt:32768:8:1$o5bINITJIUXN2zrS$89017deb84020731240829980fa0496a6884731a506d23553ad22c46267e96d3bf03f7ee40d4ec0af3c72903cc774b48413c3eb02ffed5724a191d2f0bac178a	user	160	aprovado	(13) 99621-9222	1971-02-17	11	0	097.844.848-03	22.683.028-7	\N	\N	\N	Servente	t	2025-07-25
12	Nubia Toledo	51065	nubia.toledo@live.com	pbkdf2:sha256:1000000$p8xJvk6gGovJ6rCr$c0c5dfd09d1206e8828f4fa0b867fd7b2fafea730f60ab559245d453b9431fb2	user	370	aprovado	(11) 96081-4553	1997-08-31	0	0	466.022.178-44	45.681.224-6	2015-03-15	SSP	Tecnólogo	Agente Administrativo	t	2025-07-25
17	Márcio dos Santos Freitas 	51215	msfreitas71@hotmail.com	pbkdf2:sha256:1000000$qAjqTqJenBFhl76W$a3e29599249a7af94f71d8aae50905f63c3161a3a45cfcde6a6c2f58f5507a09	user	0	aprovado	(13) 98817-4736	1971-08-06	5	0	159.124.408-00	20.954.000-_	\N	SSP-SP	Pós Graduação Latu Sensu	Atendente de Educação I	t	2025-07-25
25	MICHELLE CARDOSO RAMOS DOS SANTOS	23459	chellelucassantos@gmail.com	pbkdf2:sha256:1000000$ShcLDKa8b1klYk7e$622b60da982669c832c6c43075aa15e8765a27a6c2f730c1b45e12aab1421ca4	user	120	aprovado	(13) 98138-6026	1979-06-19	0	0	287.894.558-19	30.497.272-1	\N	SP	Técnico	Educador de Desenvolvimento Infanto Juvenil	t	2025-07-25
50	Maria Rosa Rodrigues Dias 	41348	rosa.sto@hotmail.com	pbkdf2:sha256:1000000$2XzFto44CPK2rPli$fad9c8568c86d931cbed29f6d942726ada85a0d7c69febce35133fd253fcf48b	user	4373	aprovado	(13) 99603-9026	1969-09-16	0	0	134.395.818-02	53.056.130-0	2013-06-05	None Santos-SP	Técnico	Servente II	t	2025-07-25
45	Moniele Abreu da Conceição 	53056	monielehelena05@gmail.com	scrypt:32768:8:1$NTDKj7cTfMDdeAkM$59ec69e0bafaa1e3602570ffdcfcebf7b1acfa8c7804b8d98eda3bdbb874d1312193ffec7266381cf5d2e3c1895f3e28022812a75386da01fbe08ed967a961b9	user	397	aprovado	(11) 96642-4610	1987-09-03	0	0	364.409.538-85	42.427.864-9	\N	None	Pós Graduação Latu Sensu	Educador de Desenvolvimento Infanto Juvenil	t	2025-07-25
74	Gabrielle Valério Florindo Conti de Moura	51679	gabrielleflorindo01@gmail.com	pbkdf2:sha256:1000000$hZNyLc32ODWydtjK$6e874e44b4e0353fd709f9663431cc134d4fa2623503b251517440b2045266c5	user	980	aprovado	(13) 99606-9832	1997-03-28	0	0	449.516.118-05	50.104.238-6	2019-11-04	Ssp	Pós Graduação Latu Sensu	Educador de Desenvolvimento Infanto Juvenil	t	2025-07-25
59	SILVANDA DIAS DO SANTOS CAETANO	50701	silvandadias9@gmail.com	pbkdf2:sha256:1000000$xbWVsun8f9Wy2Xgg$8f75a2201d3e4d38baf98684f2d4f7edc97ec60d2ed3b82fa34a6b3e40695a57	user	180	aprovado	(13) 99168-0319	1973-05-29	5	1	199.273.388-05	25.005.891-1	\N	\N	\N	Servente	t	2025-07-25
83	TATIANE BEZERRA DA SILVA	24989	tbsadvogada@gmail.com	scrypt:32768:8:1$CSF3vticTkKZlApr$0697df70498cd2a6caf7af62ce980af8c50a1b9b905f15672662ea75299ce106467b0b3a7cc14a1fe7ff596c5f2eb0a0aede98a76839f72ce9e712372226ffdd	user	0	aprovado	(13) 98130-0491	1983-01-15	0	0	315.197.308-61	42.562.504-7	\N	\N	\N	Agente Administrativo	t	2025-07-25
77	Sidicleia Cristina Ferreira Lima	50062	sidy_gui@hotmail.com	pbkdf2:sha256:1000000$FnOYu1MJNsW13yeB$8c589d8e0938e966e5628a7e7868dba9c827375e2b3f93644ca10190e30c41de	user	0	aprovado	(13) 99716-8830	1989-07-03	4	0	390.357.628-00	47.853.596-_	2021-02-18	SSP	Pós Graduação Latu Sensu	Trabalhador	t	2025-07-25
81	Thamires Vieira Silva Carvalho 	53238	tvcarvalho@educacaopg.sp.gov.br	scrypt:32768:8:1$esHGZErWRHzv7qjD$ef62b0b8212bfaa80f7ec7a8961e55c1e35ba4f1e9033427065900746703ff5ae7bae26fad78115675a431d82c84d5dbc3faf6b08696dffcab6ea0334e872388	user	0	aprovado	(13) 98156-3113	1987-08-03	0	0	360.257.958-19	36.255.922-3	2023-03-27	SSP/SP	Pós Graduação Latu Sensu	Professor III	t	2025-07-25
20	Vanessa Raquel Rodrigues Borges Amaro 	34221	vanessar.rba@hotmail.com	pbkdf2:sha256:1000000$JbPX03SgegOouW97$6d52772023db0e2003a6c349d5538c642172e77eb63e7999456d00451e851bcc	user	55	aprovado	(13) 99783-9449	1982-02-22	0	0	324.191.888-29	35.148.272-6	1982-11-22	SSPSP	Técnico	Agente Administrativo	t	2025-07-25
\.


--
-- Name: agendamento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: folgas_user
--

SELECT pg_catalog.setval('public.agendamento_id_seq', 553, true);


--
-- Name: banco_de_horas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: folgas_user
--

SELECT pg_catalog.setval('public.banco_de_horas_id_seq', 367, true);


--
-- Name: esquecimento_ponto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: folgas_user
--

SELECT pg_catalog.setval('public.esquecimento_ponto_id_seq', 104, true);


--
-- Name: folga_id_seq; Type: SEQUENCE SET; Schema: public; Owner: folgas_user
--

SELECT pg_catalog.setval('public.folga_id_seq', 1, false);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: folgas_user
--

SELECT pg_catalog.setval('public.user_id_seq', 112, true);


--
-- Name: agendamento agendamento_pkey; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.agendamento
    ADD CONSTRAINT agendamento_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: banco_de_horas banco_de_horas_pkey; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.banco_de_horas
    ADD CONSTRAINT banco_de_horas_pkey PRIMARY KEY (id);


--
-- Name: esquecimento_ponto esquecimento_ponto_pkey; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.esquecimento_ponto
    ADD CONSTRAINT esquecimento_ponto_pkey PRIMARY KEY (id);


--
-- Name: folga folga_pkey; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.folga
    ADD CONSTRAINT folga_pkey PRIMARY KEY (id);


--
-- Name: user user_cpf_key; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_cpf_key UNIQUE (cpf);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_registro_key; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_registro_key UNIQUE (registro);


--
-- Name: user user_rg_key; Type: CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_rg_key UNIQUE (rg);


--
-- Name: agendamento agendamento_funcionario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.agendamento
    ADD CONSTRAINT agendamento_funcionario_id_fkey FOREIGN KEY (funcionario_id) REFERENCES public."user"(id);


--
-- Name: banco_de_horas banco_de_horas_funcionario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.banco_de_horas
    ADD CONSTRAINT banco_de_horas_funcionario_id_fkey FOREIGN KEY (funcionario_id) REFERENCES public."user"(id);


--
-- Name: esquecimento_ponto esquecimento_ponto_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.esquecimento_ponto
    ADD CONSTRAINT esquecimento_ponto_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: folga folga_funcionario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: folgas_user
--

ALTER TABLE ONLY public.folga
    ADD CONSTRAINT folga_funcionario_id_fkey FOREIGN KEY (funcionario_id) REFERENCES public."user"(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON SEQUENCES TO folgas_user;


--
-- Name: DEFAULT PRIVILEGES FOR TYPES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TYPES TO folgas_user;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON FUNCTIONS TO folgas_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO folgas_user;


--
-- PostgreSQL database dump complete
--

\unrestrict EIv9Fz9RpqUJewi36ceR42EDeZ7q53a9jDJocKAmg6FNOF7owcEbrcT3W0wc9Gd

