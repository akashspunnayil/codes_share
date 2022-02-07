#Data generation
Year <- c(2014, 2015, 2016)
Response <- c(1000, 1100, 1200)
Rate <- c(0.75, 0.42, 0.80)

df <- data.frame(Year, Response, Rate)

#Chart
library(ggplot2)

ggplot(df)  + 
  geom_bar(aes(x=Year, y=Response),stat="identity", fill="tan1", colour="sienna3")+
  geom_line(aes(x=Year, y=Rate),stat="identity")+
  geom_text(aes(label=Rate, x=Year, y=Rate), colour="black")+
  geom_text(aes(label=Response, x=Year, y=0.9*Response), colour="black")