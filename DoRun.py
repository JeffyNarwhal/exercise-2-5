from collections.abc import Callable
from typing import Final, TypedDict
import numpy as np
import random

class Run(TypedDict):
    timesOptimalLeverIsChosen: int
    averageReward: float

def run(useIncrementalEstimateCalculation: bool) -> Run:
    DEFAULT_ESTIMATE: Final = 0
    CHANCE_TO_SELECT_RANDOMLY: Final = 0.1
    ARE_LEVERS_WALKING: Final = True

    NUMBER_OF_ITERATIONS: Final = 10000

    STEP_SIZE_PARAMETER: Final = 0.1

    # Page 31 Second Edition Barto and Sutton
    def calculateNewAverageIncrementally(oldAverage, nextValue, numberOfValues):
        return oldAverage + (1/numberOfValues) * (nextValue - oldAverage)

    def calculateNewAverageWithStepSizeParameter(oldAverage, nextValue, stepSizeParameter):
        return oldAverage + (stepSizeParameter) * (nextValue - oldAverage)

    class Lever(TypedDict):
        estimate: None | float
        getReward: Callable[[], float]
        takeRandomWalk: Callable[[], None]
        getTrueValue: Callable[[], float]

    def createLever() -> Lever:
        trueValue = np.random.normal(0, 1)
        def takeRandomWalk():
            nonlocal trueValue
            trueValue += np.random.normal(0, 0.01)
        return {
            # Really should just use 0 as the starting value rather than None
            "estimate": None,
            "getReward": lambda: np.random.normal(trueValue, 1),
            "takeRandomWalk": takeRandomWalk,
            "getTrueValue": lambda: trueValue
        }

    def getOptimalLever(levers: list[Lever]):
        optimalLever = levers[0]
        for lever in levers:
            if (optimalLever["getTrueValue"]() < lever["getTrueValue"]()):
                optimalLever = lever
        return optimalLever

    def chooseLeverRandomly():
        return random.choice(levers)

    def chooseLeverGreedily():
        def getHighestEstimateLevers(list: list[Lever]) -> list[Lever]:
            highestEstimate = -999
            highestEstimateLevers = []
            for _,lever in enumerate(list):
                estimate = lever['estimate'] if lever['estimate'] is not None else DEFAULT_ESTIMATE
                if (estimate > highestEstimate):
                    highestEstimateLevers = []
                    highestEstimate = estimate
                    highestEstimateLevers.append(lever)
                elif(estimate == highestEstimate):
                    highestEstimateLevers.append(lever)
            return highestEstimateLevers

        highestEstimateLevers = getHighestEstimateLevers(levers)
        return random.choice(highestEstimateLevers)

    levers = [
        createLever(),
        createLever(),
        createLever(),
        createLever(),
        createLever(),
        createLever(),
        createLever(),
        createLever(),
        createLever(),
        createLever(),
    ]

    averageReward: float = 0

    optimalLever = getOptimalLever(levers)
    timesOptimalLeverIsChosen = 0

    for i in range(NUMBER_OF_ITERATIONS):
        def chooseLever():
            if (random.random() < CHANCE_TO_SELECT_RANDOMLY):
                return chooseLeverRandomly()
            else:
                return chooseLeverGreedily()

        def updateEstimate(lever, reward):
            if (lever['estimate'] is None):
                lever['estimate'] = reward
            else:
                if (useIncrementalEstimateCalculation):
                    lever['estimate'] = calculateNewAverageIncrementally(lever['estimate'], reward, i + 1)
                else:
                    lever['estimate'] = calculateNewAverageWithStepSizeParameter(lever['estimate'], reward, STEP_SIZE_PARAMETER)

        def updateAverageRewards(reward):
            nonlocal averageReward
            if (i == 0):
                averageReward = reward
            else:
                averageReward = calculateNewAverageIncrementally(averageReward, reward, i + 1)

        def walkLevers():
            if (ARE_LEVERS_WALKING):
                for _,lever in enumerate(levers):
                    lever["takeRandomWalk"]()

        lever = chooseLever()
        reward = lever['getReward']()

        if (lever is optimalLever):
            timesOptimalLeverIsChosen += 1

        updateEstimate(lever, reward)
        updateAverageRewards(reward)
        walkLevers()

    return {
        "timesOptimalLeverIsChosen": timesOptimalLeverIsChosen,
        "averageReward": averageReward
    }
