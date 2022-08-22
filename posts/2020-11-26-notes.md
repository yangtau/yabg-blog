---
author: τ
title: 数据库学习笔记
date: 2020-11-26
template: post-code-math
hide: true
---

## Data Models

A <u>data model</u> is collection of concepts for describing the data in a database.

A <u>schema</u> is a description of a particular collection of data, using a given data model.

**Data Models:**

- Relational
- Key/Value
- Graph
- Document
- Column-family
- Hierarchical
- Network
- Multi-Value

### Relational Model

A <u>relation</u> is unordered set that contain the relationship of attributes that represent entities.

A <u>tuple</u> is a set of attribute values in the relation.

#### Keys

A relation's <u>primary key</u> uniquely identifiers a single tuple.

A <u>foreign key</u> specifies that an attribute from one relation has to map to a tuple in another relation.

#### Relational Algebra

- **Select**: Choose a subset of the tuples from a relation that satisfies a selection predicate.

  $$\sigma_{predicate}(R)$$

- **Projection**: Generate a relation with tuples that contains only the specified attributes.

  $$\pi_{A_1, A_2, ..., A_n}(R)$$

- **Union**:

  $$R \cup S$$

- **Intersection**:

  $$R \cap S$$

- **Diffrence**: Generate a relation that contains only the tuples that appear in the first and not the second of the input relations.

  $$R-S$$

- **Product**: Generate a relation that contains all possible combinations of tuples from the input relations.

  $$R \times S$$

- **Join**: Generate a relation  that contains all tuples that are a combination of two tuples with a common value(s) for one or more attributes.

  $$R\bowtie S$$

- **Rename**:

  $$\rho$$

- **Assignment**:

  $$R \leftarrow S$$

- **Duplicate Elimination**:

  $$\delta (R)$$

- **Aggregation**:

  $$\gamma$$

- **Sorting**:

  $$\tau$$

- **Division**:

  $$R \div S$$

## SQL

