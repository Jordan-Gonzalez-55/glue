import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Path to the input CSV file in S3
s3_input_path = "s3://glue-input-jordan/scripts/products.csv"

print("========== Starting Glue Job V1==========")

# Read CSV as a DynamicFrame
print("Reading CSV file from S3...")
dyf = glueContext.create_dynamic_frame.from_options(
    format_options={"withHeader": True, "separator": ","},
    connection_type="s3",
    format="csv",
    connection_options={"paths": [s3_input_path]},
    transformation_ctx="dyf"
)

print("Successfully loaded data into DynamicFrame.")

# Convert to Spark DataFrame
df = dyf.toDF()
print("Converted DynamicFrame to Spark DataFrame.")

# Show the first 10 rows in CloudWatch logs
print("========== DataFrame Preview ==========")
df.show(10, truncate=False)
print("========== End of Preview ==========")

glueContext.write_dynamic_frame.from_options(
    frame=dyf,
    connection_type="s3",
    format="parquet",
    connection_options={"path": "s3://glue-input-jordan/scripts/products_output.parquet"},
    transformation_ctx="datasink"
)


job.commit()
print("========== Glue Job Completed Successfully ==========")
