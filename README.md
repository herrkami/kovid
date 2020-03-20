# kovid

Some custom data analysis on COVID-19 data. **Please don't interpret/spread/use/publish these plots without fully understanding them!!!**

## Why?
Data that is currently being distributed by news papers and info charts mostly shows absolute numbers, which I find not very helpful for comparing different countries. Also it usually does not include critical numbers such as the hospital capacities and so on.

## How?
The folder contains an `update.sh` script that clones/pulls from the [CSSE](https://github.com/CSSEGISandData/COVID-19.git) repository.

## What?
Three plots are generated:
- confirmed cases per capita
- estimated cases per capita based on the deaths per capita
- spread rate

### confirmed cases per capita
This is the number of registered confirmed cases divided by the population size. This number is suspected to lag around 7 - 9 days behind the actual infections because the average incubation period is 5 days and there is a 2 - 4 days delay for testing and registration. Since the growth rate for most countries with an exponential outbreak is currently around 30%, this number can be multiplied by approximately 10 to get an estimate of the actual number of currently infected people.

The dashed lines indicate **very rough estimates** of the ICU capacities for COVID-19 patients in each country. E.g. Germany has 29.2 ICUs per 100,000 people with a default occupancy (i.e. non-Corona patients) of 80%. Therefore, these are only 0.2*29.2 = 5.84 ICUs for the Corona patients. Moreover, approximately 6% of the COVID-19 infected require ICU treatment. Thus, 0.097% of the population can maximally become sick simultaneously. Every country (that is cherry-picked in the `python` script) has an ICU capacity attached to it that I gathered from those two sources:
- https://link.springer.com/article/10.1007/s00134-012-2627-8
- https://link.springer.com/article/10.1007/s00134-015-4165-7
In addition it get's multiplied by 0.2. This is probably too high for countries like Germany because they can increase their ICU capacity easily by shifting non-urgent operations. On the other hand, it is probably too high countries like the UK because their ICU rate is already only one fifth of the German capacity, so less operations can be shifted easily.

### estimated cases per capita based on the deaths per capita
The number of deaths per country is considered to be more reliable than the number of positive test results because
1. not everyone who is infected can be tested
2. on the other hand, deaths are usually registered
3. countries have largely varying test capacities which is directly reflected in the large variation of average death rates per country

To make the country comparison more reliable, I found it therefore useful to estimate the number of actual cases based on the death rate that is found in the countries with the largest test capacities: Germany and South Korea. Here, we have seen approximately 0.2% during exponential growth.

Note that this estimate only holds true during the exponential growth phase! This is because the death rate reflects the number people that died from infections that happened a few days earlier. To understand this, assume that the spread would suddenly stop and the number of infections would suddenly stay constant. The number of deaths would then still increase because people were already sick. Thus, 0.2% is not the true death rate of COVID-19 but only the fraction of the current number of deaths in relation to the currently registered cases during the exponential phase.

### spread rate
This is the number of newly registered infections divided by the number of confirmed infections from the day before.
