# Master-metered Violation Tracker Application (MMVT)
City of Georgetown Water Utility Analytics Team

## Overview

Our team has been tasked with analysis and resulting software for a budget-based conservation approach for master-metered customers. The objectives are:  

1. Provide an equitability study on the approach as it compares to existing customers who are receiving irrigation violations using the wrong-day approach
2. Develop a tool or application to assist Conservation staff with administering this approach

## Method

To perform both objectives, we will need to first develop the approach for assessing the water budget and compare it to the existing approach (wrong-day watering). water_budget.py will be developed with sufficient flexibility to be used for this purpose initially.

### Terms and Definitions

**Analysis period:**  
The analysis period is the span of time for each given analysis. This period must be comprised of one or more week periods.

**Week period:**
Each analysis period is made oup of one or more week periods, comprised of seven day periods and using a Monday-Monday week structure.

**Day period:**
Each day period is a twenty-four hour period from 00:00:00 - 24:00:00.

**Drought contingency modifiers and reference table:**

The irrigation coverage depth, $i$, is introduced via lookup from the Drought Contingency Plan (DCP) reference table:

|DCP Argument|Irrigation Depth in Inches|No Water Window Min| No Water Window Max|
|------------|----------------|-------------------|--------------------|
|           0|               1|               null|                null|
|           1|            0.75|               0900|                1900|
|           2|             0.5|               0700|                1900|
|           3|               0|               0000|                2400|
|           4|               0|               0000|                2400|

In addition, the No Water Window Min and No Water Window Max values are used to assess watering window violations.

**Irrigation Meter**
The currently active meter assigned to an active contract with the `Irrigation` product type in UMAX.

**Domestic Meter**
Any active meters assigned to active contracts with a billing classification of `Water` and a product other than `Irrigation`.

## Violations

### Monday watering violation

Any week period in the given analysis period where a customer's irrigation meter(s) register > 0 gallons in an interval whose date is a Monday will be flagged for a Monday Watering Violation

### Water budget calculation and violation

Water budgets will be calculated by taking as argument the area in square feet of irrigatable land for a given customer and calculating a weekly allowance based on 1" of irrigation over the totality of that acreage.

Where $b$ is the weekly water budget,   
$a$ is the square feet of irrigatable land,  
$i$ is the irrigation coverage depth in inches,  
$\gamma$ a constant of 7.48 gallons per cubic foot

$$
b = a * (i / 12) * \gamma / 1000
$$

In this calculation, $a$ is multiplied by $i$ to calculate a volume in cubic feet. $i$ is determined from the DCP reference table. The volume in cubic feet is then converted to gallons by multiplying by the constant $\gamma$. Finally, the product is converted into kgals by dividing by 1000.

This value becomes the weekly water budget for the customer during subsequent analysis.

In a given analysis period, in a given week period within that analysis period, if the customer's weekly sum of consumption between irrigation and domestic meters is greater than $b$, that week is flagged with a budget overage violation.

### Watering Window Violation

For each interval read in each day period in the analysis period, if the interval hour is between the No Water Min and No Water Max hours for the selected DCP stage from the DCP reference table, then watering window violation is flagged.

## Equitability

To study the equitability of this method, a study of historical wrong-day watering cases will evaluated based upon the method described in this document. The results of this study will be used to identify equitability between the methods by comparing the frequency of historical cases which would receive a violation under the budget-based approach to those which would not.

Further experimentation will be done to compare a statistically significant set of random cases.

## Software

The MMVT application is written in Python 3.12.

The basic logic of the program is this:
1. The program requests the user for a data file, a date, report type, and the current DCP stage.
2. The program loads the user file.
3. The program goes from customer to customer in the user file, and for each, processes total violations of all types.
4. The program outputs the violation counts to a formatted Excel file, and, if requested, a simplified report of all meter reads for a single customer.

The program is designed to be used with a specific input file that provides the customer's account number and meter identifiers. The program is also designed to cover a single week in retrospect. 

