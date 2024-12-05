from lib.state.schemes.chart import ProjectStateChart


class ProjectPlanChart:
    def __init__(self, action: str, chart: ProjectStateChart, chart_current: ProjectStateChart or None = None):
        self.action: str = action
        self.chart: ProjectStateChart = chart
        self.chart_current: ProjectStateChart or None = chart_current

    def get_action(self) -> str:
        return self.action

    def is_action(self, *actions: str) -> bool:
        for action in actions:
            if action.strip().lower() == self.get_action():
                return True
        return False

    def get_chart(self) -> ProjectStateChart:
        return self.chart

    def get_current_chart(self) -> ProjectStateChart or None:
        return self.chart_current

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "chart": self.chart,
            "chart_current": self.chart_current,
        }