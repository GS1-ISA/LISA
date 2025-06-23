# Knowledge Graph Schema for GS1 Standards

## Objective

This document defines the Knowledge Graph (KG) schema for GS1 Standards, focusing on core GS1 identification keys (GTIN, GLN, SSCC) and their immediate related entities (Products, Locations, Logistic Units).

## Scope

The schema primarily covers `GS1_Standard` entities, `Product`, `Location`, `LogisticUnit`, and `Organization`, along with the core GS1 identification keys: GTIN, GLN, and SSCC.

---

## 1. Core Entities

The primary entities in the Knowledge Graph are:

*   **`GS1_Standard`**: Represents a specific GS1 standard document or specification.
*   **`Product`**: Represents a trade item identified by a GTIN.
*   **`Location`**: Represents a physical location or legal entity identified by a GLN.
*   **`LogisticUnit`**: Represents a logistic unit (e.g., pallet, case) identified by an SSCC.
*   **`Organization`**: Represents a company or entity involved in the supply chain, publishing standards, owning products, or operating locations.
*   **`IdentificationKey`**: An abstract entity representing the concept of a GS1 identification key (GTIN, GLN, SSCC).
*   **`Attribute`**: Represents a property or characteristic of an entity or relationship.

---

## 2. Relationships

The relationships between these entities capture how they interact and connect within the GS1 ecosystem:

*   **`ORGANIZATION` -- `publishes` --> `GS1_STANDARD`**: An organization (e.g., GS1 Global) publishes a specific GS1 standard.
*   **`ORGANIZATION` -- `owns` --> `PRODUCT`**: An organization is the brand owner or manufacturer of a product.
*   **`ORGANIZATION` -- `operates` --> `LOCATION`**: An organization operates a specific location (e.g., a warehouse, store).
*   **`GS1_STANDARD` -- `defines` --> `IDENTIFICATION_KEY`**: A GS1 standard defines the structure and usage of an identification key (e.g., the General Specifications define GTINs).
*   **`PRODUCT` -- `identifiedBy` --> `GTIN`**: A product is uniquely identified by a GTIN.
*   **`LOCATION` -- `identifiedBy` --> `GLN`**: A location is uniquely identified by a GLN.
*   **`LOGISTIC_UNIT` -- `identifiedBy` --> `SSCC`**: A logistic unit is uniquely identified by an SSCC.
*   **`PRODUCT` -- `hasAttribute` --> `ATTRIBUTE`**: A product possesses various attributes (e.g., color, size, weight).
*   **`GS1_STANDARD` -- `appliesTo` --> `PRODUCT`**: A GS1 standard is applicable to a product (e.g., a standard for product identification).
*   **`GS1_STANDARD` -- `appliesTo` --> `LOCATION`**: A GS1 standard is applicable to a location (e.g., a standard for location identification).
*   **`GS1_STANDARD` -- `appliesTo` --> `LOGISTIC_UNIT`**: A GS1 standard is applicable to a logistic unit.
*   **`LOGISTIC_UNIT` -- `contains` --> `PRODUCT`**: A logistic unit contains one or more products.
*   **`LOGISTIC_UNIT` -- `contains` --> `LOGISTIC_UNIT`**: A logistic unit can contain other logistic units (e.g., a pallet contains cases).

---

## 3. Attributes for Each Entity and Relationship

### Entities:

*   **`GS1_Standard`**
    *   `standardId`: Unique identifier for the standard (e.g., "GS1 General Specifications", "GS1 Digital Link"). (Type: String)
    *   `version`: Version number of the standard (e.g., "23.0.1"). (Type: String)
    *   `publicationDate`: Date the standard was published. (Type: Date)
    *   `description`: A brief summary of the standard's purpose. (Type: String)
    *   `url`: Link to the official standard document. (Type: URL)

*   **`Product`**
    *   `name`: Common name of the product. (Type: String)
    *   `description`: Detailed description of the product. (Type: String)
    *   `brand`: Brand name of the product. (Type: String)
    *   `category`: Product category (e.g., "Food", "Electronics"). (Type: String)
    *   `packagingType`: Type of packaging (e.g., "Box", "Bottle"). (Type: String)
    *   `netContent`: Net content of the product (e.g., "500g", "1L"). (Type: String)

*   **`Location`**
    *   `name`: Name of the location (e.g., "Main Warehouse", "Store #123"). (Type: String)
    *   `address`: Full street address. (Type: String)
    *   `city`: City of the location. (Type: String)
    *   `country`: Country of the location. (Type: String)
    *   `latitude`: Geographical latitude. (Type: Float)
    *   `longitude`: Geographical longitude. (Type: Float)

*   **`LogisticUnit`**
    *   `description`: A general description of the logistic unit (e.g., "Standard Pallet", "Shipping Case"). (Type: String)
    *   `type`: Specific type of logistic unit (e.g., "Pallet", "Case", "Crate"). (Type: String)
    *   `dimensions`: Dimensions of the logistic unit (e.g., "120x80x145 cm"). (Type: String)

*   **`Organization`**
    *   `name`: Legal name of the organization. (Type: String)
    *   `type`: Role of the organization (e.g., "Manufacturer", "Retailer", "Logistics Provider", "GS1 Member Organization"). (Type: String)
    *   `website`: Organization's official website. (Type: URL)

*   **`IdentificationKey`** (Abstract - specific instances are GTIN, GLN, SSCC)
    *   `value`: The actual numerical or alphanumeric identifier (e.g., "01234567890128"). (Type: String)
    *   `type`: The specific type of identification key (e.g., "GTIN", "GLN", "SSCC"). (Type: String)
    *   `checksum`: The calculated checksum digit (if applicable). (Type: Integer)

*   **`Attribute`**
    *   `name`: Name of the attribute (e.g., "Color", "Weight", "Expiration Date"). (Type: String)
    *   `value`: The value of the attribute (e.g., "Red", "10 kg", "2025-12-31"). (Type: Any)
    *   `unit`: Unit of measurement for numerical values (e.g., "kg", "cm", "L"). (Type: String, Optional)
    *   `dataType`: The data type of the attribute's value (e.g., "String", "Integer", "Float", "Date"). (Type: String)

### Relationships (Attributes on relationships):

*   **`contains` (on `LOGISTIC_UNIT` -- `contains` --> `PRODUCT` or `LOGISTIC_UNIT`)**
    *   `quantity`: The number of products or logistic units contained. (Type: Integer)

---

## 4. Conceptual Model (Mermaid Diagram)

```mermaid
erDiagram
    ORGANIZATION ||--o{ GS1_STANDARD : publishes
    ORGANIZATION ||--o{ PRODUCT : owns
    ORGANIZATION ||--o{ LOCATION : operates
    GS1_STANDARD ||--o{ IDENTIFICATION_KEY : defines
    PRODUCT ||--o{ GTIN : identifiedBy
    LOCATION ||--o{ GLN : identifiedBy
    LOGISTIC_UNIT ||--o{ SSCC : identifiedBy
    PRODUCT ||--o{ ATTRIBUTE : hasAttribute
    GS1_STANDARD ||--o{ PRODUCT : appliesTo
    GS1_STANDARD ||--o{ LOCATION : appliesTo
    GS1_STANDARD ||--o{ LOGISTIC_UNIT : appliesTo
    LOGISTIC_UNIT ||--o{ PRODUCT : contains
    LOGISTIC_UNIT ||--o{ LOGISTIC_UNIT : contains

    IDENTIFICATION_KEY {
        string value
        string type
        string checksum
    }
    GTIN {
        string value
    }
    GLN {
        string value
    }
    SSCC {
        string value
    }
    PRODUCT {
        string name
        string description
        string brand
        string category
        string packagingType
        string netContent
    }
    LOCATION {
        string name
        string address
        string city
        string country
        float latitude
        float longitude
    }
    LOGISTIC_UNIT {
        string description
        string type
        string dimensions
    }
    ORGANIZATION {
        string name
        string type
        url website
    }
    GS1_STANDARD {
        string standardId
        string version
        date publicationDate
        string description
        url url
    }
    ATTRIBUTE {
        string name
        any value
        string unit
        string dataType
    }