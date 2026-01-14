SELECT "shopapp_products"."id",
       "shopapp_products"."name",
       "shopapp_products"."description",
       "shopapp_products"."price",
       "shopapp_products"."discount",
       "shopapp_products"."created_at",
       "shopapp_products"."archived",
       "shopapp_products"."created_by_id",
       "shopapp_products"."preview"
FROM "shopapp_products"
WHERE NOT "shopapp_products"."archived"
ORDER BY "shopapp_products"."name" ASC,
         "shopapp_products"."price" ASC;


SELECT "shopapp_products"."id",
       "shopapp_products"."name",
       "shopapp_products"."description",
       "shopapp_products"."price",
       "shopapp_products"."discount",
       "shopapp_products"."created_at",
       "shopapp_products"."archived",
       "shopapp_products"."created_by_id",
       "shopapp_products"."preview"
FROM "shopapp_products"
WHERE "shopapp_products"."id" = 2
LIMIT 21;

SELECT "shopapp_productimages"."id",
       "shopapp_productimages"."product_id",
       "shopapp_productimages"."image",
       "shopapp_productimages"."description"
FROM "shopapp_productimages"
WHERE "shopapp_productimages"."product_id" IN (2);

SELECT "shopapp_orders"."id",
       "shopapp_orders"."delivery_address",
       "shopapp_orders"."promocode",
       "shopapp_orders"."created_at",
       "shopapp_orders"."user_id",
       "shopapp_orders"."receipt",
       (CAST(SUM("shopapp_products"."price") AS NUMERIC)) AS "total",
       COUNT("shopapp_orders_products"."products_id")     AS "products_count"
FROM "shopapp_orders"
         LEFT OUTER JOIN "shopapp_orders_products" ON ("shopapp_orders"."id" = "shopapp_orders_products"."orders_id")
         LEFT OUTER JOIN "shopapp_products" ON ("shopapp_orders_products"."products_id" = "shopapp_products"."id")
GROUP BY "shopapp_orders"."id", "shopapp_orders"."delivery_address", "shopapp_orders"."promocode",
         "shopapp_orders"."created_at", "shopapp_orders"."user_id", "shopapp_orders"."receipt";


SELECT "shopapp_orders"."id",
       "shopapp_orders"."delivery_address",
       "shopapp_orders"."promocode",
       "shopapp_orders"."created_at",
       "shopapp_orders"."user_id",
       "shopapp_orders"."receipt",
       (CAST(COALESCE((CAST(SUM("shopapp_products"."price") AS NUMERIC)),
                      (CAST('0' AS NUMERIC))) AS NUMERIC)) AS "total",
       COUNT("shopapp_orders_products"."products_id")      AS "products_count"
FROM "shopapp_orders"
         LEFT OUTER JOIN "shopapp_orders_products" ON ("shopapp_orders"."id" = "shopapp_orders_products"."orders_id")
         LEFT OUTER JOIN "shopapp_products" ON ("shopapp_orders_products"."products_id" = "shopapp_products"."id")
GROUP BY "shopapp_orders"."id", "shopapp_orders"."delivery_address", "shopapp_orders"."promocode",
         "shopapp_orders"."created_at", "shopapp_orders"."user_id", "shopapp_orders"."receipt";