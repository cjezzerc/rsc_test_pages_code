[Go to Codelist Index]({{ rel_path_to_codelists_index }})

# SPEARATE TEMPLATE FILE Phenotype Index

| id | title | brief description | codelists used | templates used |
|----|-------|-------------------|----------------|----------------|
{%- for p_id in p_ids_sorted %} 
    {%- set p = phenotypes[p_id] %} 
| {{ phenotype_hyperlinks[p.id] }} | {{p.title}} | {{ p.brief_description }} | {{codelist_hyperlinks[p.id]}}| {{template_hyperlinks[p.id]}} |
    {%- endfor %}