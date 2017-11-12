library (tidyverse)
library (pool)
library (DBI)


pool <- dbPool(
  drv = RMySQL::MySQL(),
  dbname = "atxhackathon",
  host="atxhackathon.chs2sgrlmnkn.us-east-1.rds.amazonaws.com",
  username="", 
  password=""
)

df <- pool %>% tbl("bill_votes_leg") %>% collect()
leg <- pool %>% tbl("Representative") %>% collect()

df <- df %>% left_join(leg,by="leg_id")

manip <- df %>% mutate(subjectclass= ifelse (grepl("Health",subjects),"Health","")) %>% 
  mutate(subjectclass=ifelse(grepl("Education",subjects),"Education",as.character(subjectclass))) %>% 
  mutate(subjectclass=ifelse(grepl("Environment",subjects),"Environment",as.character(subjectclass))) %>%
  mutate(repuyes=ifelse(vote=="yes" & party=="Republican",1,0)) %>% mutate(demyes=ifelse(vote=="yes" & party=="Democrat",1,0)) %>% 
  mutate(repuno=ifelse((vote=="no"|vote=="other") & party=="Republican",1,0)) %>% mutate(demno=ifelse((vote=="no" | vote=="other") & party=="Democrat",1,0))

billlevel <- manip %>% group_by(bill_id,subjectclass) %>% summarize(repuyes=sum(repuyes,na.rm=TRUE),demyes=sum(demyes,na.rm=TRUE),
                                                                    repuno=sum(repuno,na.rm=TRUE),demno=sum(demno,na.rm=TRUE))
billlevel$totalvotes <- rowSums(billlevel[,3:6])
billlevel <- billlevel %>% filter(totalvotes>2)

billlevel <- billlevel %>% mutate(dpercentyes=demyes/totalvotes) %>%
  mutate(dpercentno=demno/totalvotes) %>% mutate(rpercentyes=repuyes/totalvotes) %>% mutate(rpercentno=repuno/totalvotes) %>% 
  mutate_if(is.numeric, funs(round(., 2))) %>% mutate(progressive=ifelse(rpercentyes<=.5,1,0))

copy_to(pool, billlevel, "billscore",
        temporary = FALSE, 
        indexes = list(
          "bill_id", 
          "subjectclass", 
          "progressive", 
          "totalvotes"
        )
)

df <- pool %>% tbl("billscore")
df
