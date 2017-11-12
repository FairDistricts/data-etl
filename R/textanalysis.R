library (pool)
library (DBI)
library (tidyverse)
library (tidytext)

pool <- dbPool(
  drv = RMySQL::MySQL(),
  dbname = "atxhackathon",
  host="atxhackathon.chs2sgrlmnkn.us-east-1.rds.amazonaws.com",
  username="", 
  password=""
)

df <- pool %>% tbl("billtext") %>% collect()
poolClose(pool)

s_score <- function (text) {
  text_df <- data_frame(line=1,text=text)
  text_df <- text_df %>% unnest_tokens(word,text) %>% mutate(word=as.factor(word))
  text_df$word <- gsub(" ", "", text_df$word, fixed = TRUE)
  
  text_df <- text_df %>% mutate(filterable=ifelse(nchar(word)<=1 & is.na(as.numeric(word)),1,0)) %>% 
    filter(filterable==0) %>% select (-filterable)
  
  text_df <- text_df %>% anti_join(stop_words, by="word")
  
  billsentiment <- text_df %>%
    inner_join(get_sentiments("bing"), by="word")  
  
  #print (billsentiment)

  if(nrow(billsentiment)<=1){
    return(0)
  }
  else if (dim(table(billsentiment$sentiment))==1){
      if (billsentiment$sentiment[1]=="positive"){
        pos <- nrow(billsentiment)
        return (pos)
      }
      else{
        neg <- -(nrow(billsentiment))
        return (neg)      
      }
  }
  else{
    billsentiment <- billsentiment %>% count(index = line %/% 80, sentiment) %>%
      spread(sentiment, n, fill = 0) %>%
      mutate(sentiment = positive - negative)
      #print (billsentiment)
      return(billsentiment$sentiment)
    }
}

sentiment_score_per_bill <- data_frame(bill_id=df$bill_id,
                                       text=df$text) %>% 
                                       mutate(score=map(text,s_score))

df$score <- sentiment_score_per_bill$score
#mostcommonwords <- text_df %>% count(word, sort = TRUE) %>%
#  filter(n > 15) %>%
#  mutate(word = reorder(word, n)) %>%
#  ggplot(aes(word, n)) +
#  geom_col() +
#  xlab(NULL) +
#  coord_flip()
#mostcommonwords


#get_sentiments("afinn")

#nrcjoy <- get_sentiments("nrc") %>% 
#  filter(sentiment == "joy")

#text_df %>%
#  inner_join(nrcjoy) %>%
#  count(word, sort = TRUE)

copy_to(pool, df, "billtext",
        temporary = FALSE
)

