# This your assignment report

It is a free form. you can add:

* your designs
* your answers to questions in the assignment
* your test results
* etc.

## Part 1 - Batch data ingestion pipeline

The design for the batch data ingestion is the following:

![design batch](images/batch.png)

Each tenant will generate its own files, then they will use its clientbatchingestapp to send its files to mysimbdp client-staging-input-folder. Each tenant will name its files using an identifier. Then mysimbdp will process the files in the staging folder, it will check the tenant configuration model to define if the files are correct. Then it will ingest them to coredms.

1. As platform provider I will require the following constraints to be followed.
   1. __File size limit__: up to 50 MB, use MB notation.
   2. __File type__: only CSV and JSON files are supported, they cannot be mixed.
   3. __Maximum amount of data__: 1 GB per day, use MB notation
   4. __Maximum number of files__: up to 1000 files per day not exceeding the maximum amount of data (i.e. 1000 files of 1KB, 20 files of 50MB)
  
   This information will be retrieved when the tenant when they hire the service. 
As provider, I will have a file with every tenant configuration, so I can easily add and remove tenants. 
   I will also ask for the fields that they will store in coredms, so I can add the schema in the configuration file. This will allow me to automate 
   the creation of namespaces and tables when I add a new tenant.
   The previously mentioned constraints will benefit the tenant while maintaining mysimbdp functional for the following reasons:
      * By setting the amount and size of files I can ensure that all resources are allocated  fairly for all tenants.
      * By setting amount of data per day I can make sure that my system will not be overloaded and I will ensure that each file is ingested efficiently.
      * By setting the file type I can guarantee tenants that I know how to work with them, not promising type files I have not used before.
      * By setting limits on the amount of data that can be ingested, tenants ensure they are only paying for the resources they need and not exceeding their allocated budget.
   
   The following configuration file sets two tenants with different needs:
   ```json
   {
      "tenant1": {
        "max_file_size": 10,
        "file_type": "json",
        "max_amount_of_data": 500,
        "max_number_of_files": 50,
        "namespace": "tenant1",
        "schema": {
          "created_utc": "timestamp",
          "ups": "int",
          "subreddit": "text",
          "id": "text",
          "author": "text",
          "score": "int",
          "key": "((subreddit, id), ups)"
        }
      },
    "tenant2": {
        "max_file_size": 50,
        "file_type": "csv",
        "max_amount_of_data": 1000,
        "max_number_of_files": 20,
        "namespace": "tenant2",
        "schema": {
          "created_utc": "timestamp",
          "subreddit": "text",
          "id": "text",
          "author": "text",
          "body": "int",
          "key": "((subreddit, id), author)"
        }
      }
   }   
   ```
   _Tenant 1_ will have smaller files and needs less space for their files because they only analyze the up votes of comments in 
different subreddits to reach out to authors for marketing purposes. 
On the other hand, _tenant 2_ needs bigger files and more space because they do sentiment analysis of the body of comments, which are sometimes really long. Usually csv files are smaller than json, that is why they chose that format.
2. As tenant, I will process the data obtained from the reddit API _(assumption, data will be in original-client-data)_ 
and will delete the fields that are not relevant to me, then using my clientbatchingestapp I will send files to the 
provider.
   * Tenant 1: I keep only this fields, __created_utc__ timestamp, __ups__ int, __subreddit__ text, __id__ text, __author__ text, __score__ int.
   Because that information is relevant to me. I design marketing deals for popular authors.
   * Tenant 2: I keep only this fields, __created_utc__ timestamp, __subreddit__ text, __id__ text, __author__ text, __body__ text.
   This information is relevant to me because I process the content of the comments to do sentiment analysis for research purposes.