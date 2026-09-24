-- SMALLINT solo admite valores entre -32768 y 32767.
-- Los conteos pueden superar ese límite (por ejemplo, 35180), por lo que
-- se amplían los campos numéricos de la tabla de conteos.

ALTER TABLE public.conteos
    ALTER COLUMN stock_disponible TYPE numeric USING stock_disponible::numeric,
    ALTER COLUMN conteo_fisico TYPE numeric USING conteo_fisico::numeric,
    ALTER COLUMN diferencia TYPE numeric USING diferencia::numeric;
