# OWASP Top 10 - API Security Risks

1. **Broken Object Level Authorization (BOLA)**: APIs tend to expose endpoints that handle object identifiers, creating a wide attack surface level access control issue.
2. **Broken Authentication**: Authentication mechanisms are often implemented incorrectly, allowing attackers to compromise authentication tokens or exploit implementation flaws to assume other users' identities.
3. **Broken Object Property Level Authorization**: This category combines Broken Function Level Authorization and Excessive Data Exposure.
4. **Unrestricted Resource Consumption**: Satisfying API requests requires resources such as network bandwidth, CPU, memory, and storage.
5. **Broken Function Level Authorization**: Complex access control policies with different hierarchies, groups, and roles, and an unclear separation between administrative and regular functions, tend to lead to authorization flaws.
6. **Unrestricted Access to Sensitive Business Processes**: APIs exposing business processes - such as purchasing a ticket, or posting a comment - may be harmed if an attacker automates the access to them.
7. **Server Side Request Forgery (SSRF)**: SSRF flaws occur when an API is fetching a remote resource without validating the user-supplied URI.
8. **Security Misconfiguration**: APIs and the systems supporting them typically contain complex configurations, meant to make the APIs more customizable.
9. **Improper Inventory Management**: APIs tend to expose more endpoints than traditional web applications, making proper and updated documentation highly important.
10. **Unsafe Consumption of APIs**: Developers tend to trust data received from third-party APIs more than user input, and so adopt weaker security standards.
