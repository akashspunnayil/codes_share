d<-read.csv(file.choose())
library(ggplot2)
library(scales)

d
options(scipen=1000000)# to avoid exponential value ,eg; 6e+05

nmonths = 12
x = seq(as.Date("2015/1/1"), by = "month", length.out = nmonths)# creating a fake axis for ploting Jan-Dec


gg<-ggplot(d, aes(x=x))
gg<-gg+geom_line(aes(y=d$sst_clim_total_area, colour="TF area"),size=1.1)
gg<-gg+geom_line(aes(y=d$Chl_clim_total_area, colour="CF area"),size=1.1)
gg<-gg+scale_x_date(labels=date_format("%b"))#%b is for "Jan" form of Month
#p<-p+theme(axis.text.x = element_text(angle = 90, hjust = 1))
gg<-gg + scale_colour_manual(values = c("turquoise3" , "orangered3"))
gg<-gg+labs(y="Frontal Area (sq.km)", x ="Months", colour="Frontal Area")
gg<-gg+theme_gray()+theme(text=element_text(size=20, family="TT Times New Roman"))
#gg<-gg + theme(legend.position = c(0.12,0.93))
gg<-gg + theme(legend.text=element_text(size=15))
gg<-gg+ theme(plot.margin = unit(c(1,1,1,1), "cm"))
plot(gg)


tiff("TF_CF_Climatology.tiff", width = 15, height = 8.5, units = 'in', res = 300)
plot(gg)
dev.off()
getwd()
