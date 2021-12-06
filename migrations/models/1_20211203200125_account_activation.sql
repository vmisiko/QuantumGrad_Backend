-- upgrade --
ALTER TABLE "users" ADD "email_verification_date" TIMESTAMP;
ALTER TABLE "users" ADD "is_activated" INT NOT NULL  DEFAULT 0;
ALTER TABLE "users" ADD "is_verified" INT NOT NULL  DEFAULT 0;
-- downgrade --
ALTER TABLE "users" DROP COLUMN "email_verification_date";
ALTER TABLE "users" DROP COLUMN "is_activated";
ALTER TABLE "users" DROP COLUMN "is_verified";
