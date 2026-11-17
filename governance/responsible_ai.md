\# Responsible AI Notes



Scope: the Healthcare Claims Copilot in this repository. Synthetic data only.



\## Risks and controls



| Risk | Control in this project | Gap |

|---|---|---|

| The model invents policy facts | Answers must come only from retrieved sources and must cite a file; out-of-scope questions are refused; 3 of 17 evaluation cases test refusal | Small test set |

| The model writes a harmful SQL query | SELECT-only guard plus a read-only Snowflake role; tested both ways | A guard is regex-based, so it is a second layer, not the only one |

| Prompt injection ("ignore your rules") | The router and SQL prompts treat the question as untrusted text; evaluation includes one injection case; the router fails closed to a refusal | One test case is not coverage |

| Exposure of patient-level data | Synthetic data; direct identifiers dropped in Silver; the SQL prompt asks for aggregates only | Aggregation is requested in the prompt, not enforced in code |

| Personal data in logs | The audit log stores masked questions only, and no answers | Raw text still reaches the model provider |

| Leaked credentials | Secrets live in git-ignored files; key-pair logins; separate pipeline and agent users | Local files, not a secret manager; Key Vault would be the next step |

| Runaway cost | X-Small warehouse, auto-suspend, a cap on question length, and an Azure budget alert | No per-user rate limiting |

| Wrong answers from text-to-SQL | Schema notes with business rules (for example `NO\_DX`); outputs show the SQL used so a person can check it | Answers are not independently verified |



\## Human oversight



Every database answer shows the SQL that produced it. The assistant states that it cannot answer instead of guessing.



\## Not for real use



This is a learning project. It must not be used for coverage decisions, clinical advice, or any real member data without a full privacy, security, and clinical review.



\## Next steps



1\. Mask personal data before model calls (Presidio) and enable Azure AI Content Safety.

2\. Move secrets into Azure Key Vault and use managed identities.

3\. Enforce aggregation and a minimum group size in code.

4\. Expand the evaluation set and add adversarial prompts.

5\. Add per-user authentication and rate limiting.

