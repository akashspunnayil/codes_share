library(reshape2)
library(ggplot2)
d<-read.csv(file.choose())
d

# Melting data using 'melt' function

data.m <- melt(d, id.vars='Regions')
data.m
head(data.m)
#colnames(data.m)<-c("Regions","Seasons","TF%")
#head(data.m)

a<- ggplot(data.m,aes(x=Regions, y = value)) + 
  facet_wrap(~variable) +
  geom_bar(aes(fill = factor(Regions)),position="dodge", stat = "identity", width = 0.5)
plot(a)
b<- a+theme_gray()+theme(text=element_text(size=20, family="TT Times New Roman"))
c<- b+labs(title="", x ="Regions", y = "TF area (%)",legend.title ="" )
plot(c)

# in inches
tiff("TF_percent.tiff", width = 12, height = 8, units = 'in', res = 300)
plot(c)
dev.off()
getwd()
