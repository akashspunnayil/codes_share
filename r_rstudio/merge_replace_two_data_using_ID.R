# load data
getwd()
reference_data<- read.csv("depth&levels.csv") 
reference_data
head(reference_data)

data_file <- read.csv("Model_R_below20.csv")
data_file 

head(reference_data)
head(data_file )

library(tidyverse)
result<- data_file %>% 
  left_join(reference_data, by = c("Levels" = "levels"))
write.csv(result, 'Model_R_below20_depthwise.csv', row.names = FALSE)
getwd()
