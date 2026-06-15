BEGIN;
ALTER TABLE "orders_shipment" ADD COLUMN "base_payout" numeric(10, 2) DEFAULT 0 NOT NULL;
ALTER TABLE "orders_shipment" ALTER COLUMN "base_payout" DROP DEFAULT;
CREATE TABLE "orders_deliverybatch" ("id" uuid NOT NULL PRIMARY KEY, "target_state" varchar(250) NOT NULL, "status" varchar(50) NOT NULL, "total_base_payout" numeric(10, 2) NOT NULL, "created_at" timestamp with time zone NOT NULL, "updated_at" timestamp with time zone NOT NULL, "delivery_person_id" bigint NULL);
ALTER TABLE "orders_shipment" ADD COLUMN "delivery_batch_id" uuid NULL CONSTRAINT "orders_shipment_delivery_batch_id_3ad5ccf9_fk_orders_de" REFERENCES "orders_deliverybatch"("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "orders_deliverybatch" ADD CONSTRAINT "orders_deliverybatch_delivery_person_id_a3c99959_fk_accounts_" FOREIGN KEY ("delivery_person_id") REFERENCES "accounts_delivery" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "orders_deliverybatch_delivery_person_id_a3c99959" ON "orders_deliverybatch" ("delivery_person_id");
CREATE INDEX "orders_shipment_delivery_batch_id_3ad5ccf9" ON "orders_shipment" ("delivery_batch_id");
COMMIT;
