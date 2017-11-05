library (tidyverse)
library (data.table)


election <- fread("2016_General_Election_Returns.csv")

election <- election %>%filter (Office=="President")  %>% group_by(VTD,Party) %>% summarize (sum(Votes)) %>%
  spread(Party, "sum(Votes)")

#election <- election %>%filter (Office=="President")  %>% group_by(cntyvtd,Party) %>% summarize (sum(Votes)) %>%
#  spread(Party, "sum(Votes)")# %>% mutate(C=pmax(D,G,L,R,W))

elect <- election %>% ungroup() %>% select (-VTD)
election$winner <- colnames(elect)[max.col(elect,ties.method="first")]
election$winningvotes <- pmax(elect$D, elect$G,elect$L,elect$R, elect$W)
election$totalvotes <- rowSums(election[,2:5])
election <- election %>% filter(totalvotes>0) %>% mutate(winningpercent=winningvotes/totalvotes)

percents <- c("dpercent","gpercent","lpercent","rpercent","wpercent")
originpercent <- c("D","G","L","R","W")
election$dpercent <- 0
election$gpercent <- 0
election$lpercent <- 0
election$rpercent <- 0
election$wpercent <- 0

for (i in 1:length(percents)){
  election[percents[i]] <- (election[originpercent[i]])
}

election <- election %>% mutate_if(is.numeric, funs(round(., 2))) %>% mutate(dpercent=dpercent/totalvotes) %>%
  mutate(gpercent=gpercent/totalvotes) %>% mutate(lpercent=lpercent/totalvotes) %>% mutate(rpercent=rpercent/totalvotes) %>%
  mutate(wpercent=wpercent/totalvotes) %>% mutate_if(is.numeric, funs(round(., 2)))


write.csv(election, "vtdsummary.csv")
