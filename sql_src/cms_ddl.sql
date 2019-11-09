-- Drop database CMS if exists
DROP DATABASE IF EXISTS CMS;
CREATE DATABASE CMS;
USE CMS;

-- Delete the schemas
DROP TABLE IF EXISTS Tokens;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Invoices;
DROP TABLE IF EXISTS Inventory;
DROP TABLE IF EXISTS InventoryTransactions;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS TokensSelectProducts;
DROP TABLE IF EXISTS OrdersOfProducts;
DROP TABLE IF EXISTS ProductsInInvoices;

-- Create the schemas

CREATE TABLE IF NOT EXISTS Products (
       `ProductID`       CHAR(6),
       `Name`            VARCHAR(16) NOT NULL,
       `Description`     VARCHAR(64),
       `UnitPrice`       NUMERIC(9, 3) UNSIGNED,
       `UnitType`        ENUM ("kg", "pcs", "ltrs"),
       `GST`             NUMERIC(4, 2) UNSIGNED,
       `CGST`            NUMERIC(4, 2) UNSIGNED,
       `CurrentDiscount` NUMERIC(4, 2) UNSIGNED DEFAULT 0,
       CONSTRAINT `Products_PK_FMT` CHECK (ProductID REGEXP "^[A-Z]{3}-[0-9]{2}$"),
       CONSTRAINT `Products_CUR_DSCT_FMT` CHECK (CurrentDiscount < UnitPrice),
       CONSTRAINT `Products_NAME_FMT` UNIQUE (Name),
       CONSTRAINT `Products_PK` PRIMARY KEY (ProductID)
);

CREATE TABLE IF NOT EXISTS Invoices (
       `InvoiceID`     CHAR(14),
       `InvoiceDate`   DATETIME,
       `DiscountGiven` NUMERIC(9, 3) UNSIGNED DEFAULT 0,
       `PaymentMode`   ENUM ("cash", "card", "wallet"),
       CONSTRAINT `Invoices_PK_FMT` CHECK (InvoiceID REGEXP "^INV-[0-9]{10}$"),
       CONSTRAINT `Invoices_PK` PRIMARY KEY (InvoiceID)
);

CREATE TABLE IF NOT EXISTS Tokens (
       `TokenID`   CHAR(6),
       `Assigned?` BOOLEAN DEFAULT FALSE,
       `InvoiceID` CHAR(14) DEFAULT NULL,
       CONSTRAINT `Tokens_PK_FMT` CHECK (TokenID REGEXP "^TOK-[0-9]{2}$"),
       CONSTRAINT `Tokens_PK` PRIMARY KEY (TokenID),
       CONSTRAINT `Tokens_FK` FOREIGN KEY (InvoiceID) REFERENCES Invoices (InvoiceID)
);

CREATE TABLE IF NOT EXISTS Inventory (
       `ProductID`         CHAR(6),
       `StoredQuantity`    NUMERIC(9, 3) UNSIGNED,
       `DisplayedQuantity` NUMERIC(9, 3) UNSIGNED,
       `StoreThreshold`    NUMERIC(9, 3) UNSIGNED,
       CONSTRAINT `Inventory_PK` PRIMARY KEY (ProductID),
       CONSTRAINT `Inventory_FK` FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
);

CREATE TABLE IF NOT EXISTS Orders (
       `OrderID`    CHAR(14),
       `OrderDate`  DATETIME,
       `Delivered?` BOOLEAN DEFAULT FALSE,
       `Cancelled?` BOOLEAN DEFAULT FALSE,
       CONSTRAINT `Orders_PK_FMT` CHECK (OrderID REGEXP "^ORD-[0-9]{10}$"),
       CONSTRAINT `Orders_PK` PRIMARY KEY (OrderID)
);

CREATE TABLE IF NOT EXISTS InventoryTransactions (
       `TransactionID`   CHAR(14),
       `TransactionType` ENUM ("COUNTER_SUB", "COUNTER_ADD", "INVENTORY_SUB", "INVENTORY_ADD", "INVENTORY_TO_COUNTER"),
       `ProductID`       CHAR(6),
       `Quantity`        NUMERIC(9, 3) UNSIGNED,
       `Timestamp`       DATETIME,
       CONSTRAINT `InventoryTransactions_PK_FMT` CHECK (TransactionID REGEXP "^TRC-[0-9]{10}$"),
       CONSTRAINT `InventoryTransactions_PK` PRIMARY KEY (TransactionID),
       CONSTRAINT `InventoryTransactions_FK` FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
);

CREATE TABLE IF NOT EXISTS OrdersOfProducts (
       `OrderID`   CHAR(14),
       `ProductID` CHAR(6),
       `Quantity`  NUMERIC(9, 3) UNSIGNED,
       CONSTRAINT `OrdersOfProducts_PK` PRIMARY KEY (OrderID, ProductID),
       CONSTRAINT `OrdersOfProducts_FK1` FOREIGN KEY (OrderID) REFERENCES Orders (OrderID),
       CONSTRAINT `OrdersOfProducts_FK2` FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
);

CREATE TABLE IF NOT EXISTS TokensSelectProducts (
       `TokenID`   CHAR(6),
       `ProductID` CHAR(6),
       `Quantity`  NUMERIC(9, 3) UNSIGNED,
       CONSTRAINT `TokensSelectProducts_PK` PRIMARY KEY (TokenID, ProductID),
       CONSTRAINT `TokensSelectProducts_FK1` FOREIGN KEY (TokenID) REFERENCES Tokens (TokenID),
       CONSTRAINT `TokensSelectProducts_FK2` FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
);

CREATE TABLE IF NOT EXISTS ProductsInInvoices (
       `InvoiceID` CHAR(14),
       `ProductID` CHAR(6),
       `Name`      CHAR(16),
       `Quantity`  NUMERIC(9, 3) UNSIGNED,
       `UnitPrice` NUMERIC(9, 3) UNSIGNED,
       `GST`       NUMERIC(4, 2) UNSIGNED,
       `CGST`      NUMERIC(4, 2) UNSIGNED,
       `Discount`  NUMERIC(4, 2) UNSIGNED,
       CONSTRAINT `ProductsInInvoices_PK` PRIMARY KEY (InvoiceID, ProductID),
       CONSTRAINT `ProductsInInvoices_FK1` FOREIGN KEY (InvoiceID) REFERENCES Invoices (InvoiceID),
       CONSTRAINT `ProductsInInvoices_FK2` FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
);

