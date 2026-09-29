CREATE DATABASE EcommerceDB;
GO

USE EcommerceDB;
GO

USE EcommerceDB;
GO

CREATE TABLE dbo.Superstore (
    RowID          INT,
    OrderID        VARCHAR(30),
    OrderDate      DATE,
    ShipDate       DATE,
    ShipMode       VARCHAR(50),
    CustomerID     VARCHAR(30),
    CustomerName   VARCHAR(100),
    Segment        VARCHAR(50),
    Country        VARCHAR(60),
    City           VARCHAR(60),
    State          VARCHAR(60),
    PostalCode     VARCHAR(20),
    Region         VARCHAR(30),
    ProductID      VARCHAR(40),
    Category       VARCHAR(50),
    SubCategory    VARCHAR(50),
    ProductName    VARCHAR(255),
    Sales          FLOAT,
    Quantity       INT,
    Discount       FLOAT,
    Profit         FLOAT
);
GO