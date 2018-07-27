    #----------------------------------------------------------------------
    def simpleReturn(self, n, array=False):
        """简单收益率"""
        result = (self.close[-n:] - self.close[-n-1:-1]) / self.close[-n-1:-1]
        
        if array:
            return result
        return result[-1]   
