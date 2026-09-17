# Design Specification — Fines Module
**Code:** (will be assigned when registered in document control)
**Version:** draft, no number
**Effective Date:** to be defined

## Overview

The fines module calculates the amount a user must pay when a book is returned after the agreed date. The calculation is done only once, when the return is registered, and the result is stored so that it does not change if the rate is modified later.

## Components

- `FineCalculator`: receives the loan and the actual return date, and returns the amount.
- `CurrentRate`: looks up the daily rate that was active on the day the loan expired.
- `FineRecord`: stores the amount, the date, and the user in the fines table.

## Design decisions

It was decided not to calculate fines in real time because the client asked for the amount to be fixed from the moment of return.
