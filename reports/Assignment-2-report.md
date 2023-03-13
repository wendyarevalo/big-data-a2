# This your assignment report

It is a free form. you can add:

* your designs
* your answers to questions in the assignment
* your test results
* etc.

## Part 1 - Batch data ingestion pipeline

1. As platform provider I will require the following constraints to be followed.
   1. __File size limit__: up to 50 MB, use MB notation.
   2. __File type__: only CSV and JSON files are supported, they cannot be mixed.
   3. __Maximum amount of data__: 1 GB per day, use MB notation
   4. __Maximum number of files__: up to 1000 files not exceeding the maximum amount of data (i.e. 1000 files of 1KB, 20 files of 50MB)
   
   The previously mentioned constraints will benefit the tenant while maintaining mysimbdp for the following reasons:
      * By setting the amount and size of files I can ensure that all resources are allocated  fairly for all tenants.
      * By setting amount of data per day I can make sure that my system will not be overloaded and I will ensure that each file is ingested efficiently.
      * By setting the file type I can guarantee tenants that I know how to work with them, not promising type files I have not used before.
      * By setting limits on the amount of data that can be ingested, tenants ensure they are only paying for the resources they need and not exceeding their allocated budget.
   
   The following two example files are for two tenants with different needs:
   ```json
   {
      "tenant_id": 1,
      "max_file_size": 10,
      "file_type": "csv",
      "max_amount_of_data": 500,
      "max_number_of_files": 50
   }   
   ```
   ```json
   {
      "tenant_id": 2,
      "max_file_size": 50,
      "file_type": "json",
      "max_amount_of_data": 1000,
      "max_number_of_files": 20
   }   
   ```
   _Tenant 1_ will have smaller files and needs less space for their files because they only analyze the up votes of comments in 
different subreddits to reach out to authors for marketing purposes. 
On the other hand, _tenant 2_ needs bigger files and more space because they do sentiment analysis of the body of comments, which are sometimes really long. 
2. 