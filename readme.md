# water_budget.py

City of Georgetown Water Utility Analytics Team

## Overview

Our team has been tasked with analysis and resulting software for a budget-based conservation approach for master-metered customers. The objectives are:  

1. Provide an equitability study on the approach as it compares to existing customers who are receiving irrigation violations using the wrong-day approach
2. Develop a tool or application to assist Conservation staff with administering this approach

## Method

To perform both objectives, we will need to first develop the approach for assessing the water budget and compare it to the existing approach (wrong-day watering). water_budget.py will be developed with sufficient flexibility to be used for this purpose initially.

### Terms and Definitions

**Analysis period:**  
The analysis period is the span of time for each given analysis. This period must be comprised of one or more complete Monday-to-Monday weeks.

### Water budget calculation

Water budgets will be calculated by taking as argument the acreage of irrigatable land for a given customer and calculating a weekly allowance based on 1" of irrigation over the totality of that acreage.

Where $b$ is the weekly water budget and $a$ is the acreage of irragatable land:

$$
b = a * 43560 * 0.83 * 7.48 / 1000 * c
$$

In this calculation, $a$ is first converted from acreage to square feet by multiplying the variable by 43,560. Then, the volume in cubic feet is calcuated by further multiplying this product by 0.83 (1" converted into feet). The number of gallons is then calculated using the value 7.48 (the number of gallons in a cubic foot). Finally, the product is converted into kgals by dividing by 1000.

Further calculation is needed to account for Drought Contingency

This value becomes the weekly water budget for the customer during subsequent analysis.

### Drought contingency modifier

### Irrigation violation calculation

There are two main types of irrigation violation to be considered:  

#### Monday watering violation

Monday watering violations are determined by checking the hourly interval reads of any irrigation meter associated with the account and checking for consumption on any Monday in the analysis period. If a violation is found, then the account is considered to have one wrong-day watering violation for each Monday with watering in the analysis period.

#### Budget overage violation

The resultant water budget $b$ is then compared to the sum of water consumption of all meters for the customer/property in the analysis period. If the sum of all volumes for each week in the analysis period exceeds the value $b$, then the customer is considered to have a budget overage violation for each such exceedance.

## Equitability

To study the equitability of this method, a study of historical wrong-day watering cases will evaluated based upon the method described in this document. The results of this study will be used to identify equitability between the methods by comparing the frequency of historical cases which would receive a violation under the budget-based approach to those which would not.

Further experimentation will be done to compare a statistically significant set of random cases.

## Software

## Questions
- Should we be including "commercial" meters such as clubhouse and pool meters?
- Should we use sum of all meters or only the irrigation meters?
    - Need to test both options to see how they perform.