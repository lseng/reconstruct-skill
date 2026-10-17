# Scope: {{app}} ({{platform}})

Date: {{YYYY-MM-DD}}
Slice: {{the part being rebuilt, e.g. "pages, blocks and sharing"}}
For: {{who the rebuild is for}}

## Evidence mode

Mode: {{A | B}}

- **A, public only.** Help docs, store listings, marketing pages, public API
  docs, screenshots, and the user's own account driven by the user.
- **B, authorized artifact.** Everything in A, plus REA on the shipped
  artifact: decompilation, bundle analysis, runtime and network captures.

Basis for B (one, stated by the user, not assumed):

- [ ] we own it (our own or our company's product)
- [ ] written authorization from the owner: {{engagement, contract, ticket}}
- [ ] open source under a licence that allows it: {{licence}}
- [ ] other legal basis the user has confirmed: {{what, and who confirmed}}

Licence/terms checked: {{EULA or ToS clause on reverse engineering, and what it says}}
Artifact: {{path, version, sha256}}

## Clean-room line

Evidence informs behaviour specs. It never becomes code. No decompiled code,
bundle code, assets, strings, copy or private endpoints of a third party go
into the rebuild, in either mode.
