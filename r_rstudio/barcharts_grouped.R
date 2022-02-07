library(reshape2)
library(ggplot2)
d<-read.csv(file.choose())
d

# Creating data frame 'df'

df <- data.frame(Year = c(d$Year), Sardine = c(d$Sardine), Mackerel = c(d$Mackerel))
df
head(df)

# Melting data using 'melt' function

data.m <- melt(df, id.vars='Year')
data.m
head(data.m)
colnames(data.m)<-c("Year","Species","CPUE")
head(data.m)

line_gg<-ggplot(data.m, aes(Year, CPUE)) + geom_bar(aes(fill = Species),width = 0.4, position = position_dodge(width=0.5), stat="identity") +  scale_x_continuous(breaks = seq(1998,2016,1)) +
  theme(legend.position="top")
gg<-line_gg+labs(title="Standardized CPUE", x ="Year", y = "stdsd CPUE",legend.title ="" )
plot(gg)

# in inches
tiff("CPUE of sardine and Mackerel.tiff", width = 12, height = 8, units = 'in', res = 300)
plot(gg)
dev.off()

