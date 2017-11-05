library (tidyverse)
library (pool)
library (DBI)

pool <- dbPool(
  drv = RMySQL::MySQL(),
  dbname = "atxhackathon",
  host="atxhackathon.chs2sgrlmnkn.us-east-1.rds.amazonaws.com",
  username="atxhackathon", 
  password="atxhackathon"
)

billscore <- pool %>% tbl("billscore") %>% collect ()
bill_votes <- pool %>% tbl("bill_votes_leg") %>% collect ()
legislator <- pool %>% tbl("Representative") %>% collect()

df <- billscore %>% left_join (bill_votes, by="bill_id")

manip <- df %>% select (leg_id,bill_id,progressive,subjectclass,vote) %>% filter(progressive==1) %>% 
  mutate(yesvotes=ifelse(vote=="yes",1,0)) %>% mutate(novotes=ifelse(vote=="no",1,0)) %>% 
  group_by(leg_id,progressive, subjectclass) %>% summarize(yesvotes=sum(yesvotes),novotes=sum(novotes))

##tie back to username##

final <- manip %>% left_join(legislator, by="leg_id") %>% ungroup () %>% select (-progressive)
final$totalvotes <- rowSums(final[,3:4])

final <- final %>%  mutate(percentyes=yesvotes/totalvotes) %>% mutate(percentno=novotes/totalvotes) %>% na.omit(leg_id)


copy_to(pool, final, "legislatorprogressivescore",
        temporary = FALSE, 
        indexes = list(
          "leg_id", 
          "subjectclass", 
          "district_id", 
          "party",
          "percentyes",
          "percentno"
        )
)
