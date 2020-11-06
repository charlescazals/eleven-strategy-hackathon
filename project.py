from pipelines import pipelines

class Project:
    def launch(self):
        for pipeline in pipelines:
            pipeline().launch()

if __name__=='__main__':
    Project().launch()
