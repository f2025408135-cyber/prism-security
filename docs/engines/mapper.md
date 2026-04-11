# Mapper Engine

The Authorization Topology Mapper (`prism/mapper/`) takes ingested `Endpoint` objects and systematically cross-references them against multiple `Principal` instances (e.g. Admin vs. User vs. Anonymous).

It builds a multi-dimensional matrix of authorization decisions, and extracts object IDs (UUIDs, ints, slugs) returned by successful operations.

Using `networkx`, it graphs data flow edges. If Endpoint A returns ID 123, and Endpoint B accepts ID 123 in a URL or query parameter, B implicitly depends on A. If a user can hit B without accessing A, it flags an inconsistency.
