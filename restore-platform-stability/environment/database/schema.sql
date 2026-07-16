--
-- PostgreSQL database dump
--

\restrict O8jcvzGKqKr8gA6gOcwUqUYfpc4eHy6fsjiRLyfQNBPAxFm81m9PfCkgozNXe1h

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

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
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: order_status_enum; Type: TYPE; Schema: public; Owner: ecommerce_user
--

CREATE TYPE public.order_status_enum AS ENUM (
    'PENDING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);


ALTER TYPE public.order_status_enum OWNER TO ecommerce_user;

--
-- Name: payment_status_enum; Type: TYPE; Schema: public; Owner: ecommerce_user
--

CREATE TYPE public.payment_status_enum AS ENUM (
    'PENDING',
    'SUCCESS',
    'FAILED'
);


ALTER TYPE public.payment_status_enum OWNER TO ecommerce_user;

--
-- Name: reservation_status_enum; Type: TYPE; Schema: public; Owner: ecommerce_user
--

CREATE TYPE public.reservation_status_enum AS ENUM (
    'PENDING',
    'CONFIRMED',
    'CANCELLED'
);


ALTER TYPE public.reservation_status_enum OWNER TO ecommerce_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: ecommerce_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO ecommerce_user;

--
-- Name: inventory_items; Type: TABLE; Schema: public; Owner: ecommerce_user
--

CREATE TABLE public.inventory_items (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    sku character varying(100) NOT NULL,
    quantity_available integer NOT NULL,
    price numeric(10,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_quantity_positive CHECK ((quantity_available >= 0))
);


ALTER TABLE public.inventory_items OWNER TO ecommerce_user;

--
-- Name: inventory_reservations; Type: TABLE; Schema: public; Owner: ecommerce_user
--

CREATE TABLE public.inventory_reservations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    order_id uuid NOT NULL,
    item_id uuid NOT NULL,
    quantity integer NOT NULL,
    status public.reservation_status_enum NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_reservation_quantity_positive CHECK ((quantity > 0))
);


ALTER TABLE public.inventory_reservations OWNER TO ecommerce_user;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: ecommerce_user
--

CREATE TABLE public.orders (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_id character varying(255) NOT NULL,
    total_amount numeric(10,2) NOT NULL,
    status public.order_status_enum NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.orders OWNER TO ecommerce_user;

--
-- Name: payments; Type: TABLE; Schema: public; Owner: ecommerce_user
--

CREATE TABLE public.payments (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    order_id uuid NOT NULL,
    amount numeric(10,2) NOT NULL,
    status public.payment_status_enum NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.payments OWNER TO ecommerce_user;

--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: ecommerce_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: inventory_items inventory_items_pkey; Type: CONSTRAINT; Schema: public; Owner: ecommerce_user
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_pkey PRIMARY KEY (id);


--
-- Name: inventory_reservations inventory_reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: ecommerce_user
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: ecommerce_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: ecommerce_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: ix_inventory_items_sku; Type: INDEX; Schema: public; Owner: ecommerce_user
--

CREATE UNIQUE INDEX ix_inventory_items_sku ON public.inventory_items USING btree (sku);


--
-- Name: ix_inventory_reservations_item_id; Type: INDEX; Schema: public; Owner: ecommerce_user
--

CREATE INDEX ix_inventory_reservations_item_id ON public.inventory_reservations USING btree (item_id);


--
-- Name: ix_inventory_reservations_order_id; Type: INDEX; Schema: public; Owner: ecommerce_user
--

CREATE INDEX ix_inventory_reservations_order_id ON public.inventory_reservations USING btree (order_id);


--
-- Name: ix_inventory_reservations_status; Type: INDEX; Schema: public; Owner: ecommerce_user
--

CREATE INDEX ix_inventory_reservations_status ON public.inventory_reservations USING btree (status);


--
-- Name: ix_orders_customer_id; Type: INDEX; Schema: public; Owner: ecommerce_user
--

CREATE INDEX ix_orders_customer_id ON public.orders USING btree (customer_id);


--
-- Name: ix_orders_status; Type: INDEX; Schema: public; Owner: ecommerce_user
--

CREATE INDEX ix_orders_status ON public.orders USING btree (status);


--
-- Name: ix_payments_order_id; Type: INDEX; Schema: public; Owner: ecommerce_user
--

CREATE INDEX ix_payments_order_id ON public.payments USING btree (order_id);


--
-- Name: ix_payments_status; Type: INDEX; Schema: public; Owner: ecommerce_user
--

CREATE INDEX ix_payments_status ON public.payments USING btree (status);


--
-- Name: inventory_reservations inventory_reservations_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ecommerce_user
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.inventory_items(id);


--
-- Name: payments payments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ecommerce_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- PostgreSQL database dump complete
--

\unrestrict O8jcvzGKqKr8gA6gOcwUqUYfpc4eHy6fsjiRLyfQNBPAxFm81m9PfCkgozNXe1h

