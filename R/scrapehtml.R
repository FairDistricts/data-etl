library(RCurl)
library(XML)
library (pool)
library (DBI)
library (feather)
##webscraping##

pool <- dbPool(
  drv = RMySQL::MySQL(),
  dbname = "atxhackathon",
  host="atxhackathon.chs2sgrlmnkn.us-east-1.rds.amazonaws.com",
  username="atxhackathon", 
  password="atxhackathon"
)

df <- pool %>% tbl("billscore") %>% collect()

input <- df$billtext_url
texts <- list()
for (i in 1:length(input)){
  txt <- htmlToText(input[i])
  pattern <- "<!--?\\w+((\\s+\\w+(\\s*=\\s*(?:\".*?\"|'.*?'|[^'\"-->\\s]+))?)+\\s*|\\s*)/?>"
  plain.text <- gsub(pattern, "\\1", txt)
  plain.text <- gsub('Â','',plain.text)
  plain.text <- gsub('\r\n','',plain.text)
  plain.text <- gsub('\t','',plain.text)
  texts[i] <- plain.text
}

texts

total <- tibble(bill_id = df$bill_id,bill_url=df$billtext_url, text = texts)
total <- as.data.frame(total) %>% mutate(text=as.character(text))

write_feather(total, "fortextanalys.feather")
#write.csv(total, file = "texts.csv")

copy_to(pool, total, "billtext",
        temporary = FALSE, 
        indexes = list(
          "bill_id", 
          "bill_url"
        )
)
