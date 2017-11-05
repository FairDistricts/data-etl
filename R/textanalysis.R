library (pool)
library (DBI)
library (tidyverse)

pool <- dbPool(
  drv = RMySQL::MySQL(),
  dbname = "atxhackathon",
  host="atxhackathon.chs2sgrlmnkn.us-east-1.rds.amazonaws.com",
  username="atxhackathon", 
  password="atxhackathon"
)

df <- pool %>% tbl("billtext") %>% collect()
