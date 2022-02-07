data<-read.csv(file.choose())
data
timeseries <- ts(data, frequency=12, start=c(1998,1))
timeseries
plot.ts(timeseries)
