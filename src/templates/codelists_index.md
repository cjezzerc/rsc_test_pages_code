[Go to Phenotype Index]({{ rel_path_to_phenotypes_index }})
    
# Codelist Index

| id | title | brief description | phenotypes used in |
|----|-------|-------------------|----------------|
{%- for c_id in c_ids_sorted %}
{%- set c = codelists[c_id] %} 
| {{ codelist_hyperlinks[c.id] }} | {{c.title}} | {{ c.brief_description }} | {{phenotype_hyperlinks[c.id]}}|
{%- endfor %}