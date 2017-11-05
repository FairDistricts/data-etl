library (tidyverse)
library (data.table)

legislators <- fread("tx_legislators.csv") %>% filter (active==TRUE)
rolesandparty <- fread("tx_legislator_roles.csv") %>% filter (type=="member") %>%
  group_by(leg_id) %>% filter (term==max(term))

legisfinal <- legislators %>% left_join(rolesandparty, by="leg_id") %>% filter (type=="member") %>%
  select (-district.y,-state.y,-party.y,-chamber.y)

write.csv(legisfinal,"finalwithparty.csv")



