from abc import ABC, abstractmethod


#股票策略类
class StockStrategy(ABC):
    @abstractmethod
    def analyse(self, stockCode):
        pass

    
