
from traits.api import HasTraits, Instance, Str, Property, Array, \
    on_trait_change, cached_property, List
from traitsui.api import View, Item, HGroup, EnumEditor
from enable.api import Component, ComponentEditor
from chaco.api import Plot, ArrayPlotData
from chaco.tools.api import TraitsTool, ZoomTool, PanTool

from ode import ODE, ODESolver


class ODEPlot(HasTraits):
    """ A 2D plot of ode solution variables. """
    plot = Instance(Component)
    pd = Instance(ArrayPlotData, args=())
    index_arr = Array
    value_arr = Array

    index_name = Str
    value_name = Str

    name_list = Property(List(Str), depends_on='ode.vars')

    ode = Property(Instance(ODE), depends_on='solver')
    solver = Instance(ODESolver)
    traits_view = View(Item('plot', editor=ComponentEditor(),
                            show_label=False),
                       HGroup(Item('index_name', editor=EnumEditor(name='name_list')),
                              Item('value_name', editor=EnumEditor(name='name_list'))),
                       width=800, height=700, resizable=True,
                       title="ODE Solution")

    def _get_ode(self):
        return self.solver and self.solver.ode

    @cached_property
    def _get_name_list(self):
        return ['time'] + self.ode.vars

    @on_trait_change('index_name,value_name')
    def _on_name_changed(self, obj, name, old, new):
        self._set_arr(new, name[:-5])
        if name == 'index_name':
            self.plot.x_axis.title = new
        else:
            self.plot.y_axis.title = new

    def _set_arr(self, name, key='index'):
        if name in ['t', 'time']:
            arr = self.solver.t
        elif name in self.ode.vars:
            arr = self.solver.solution[:, self.ode.vars.index(name)]
        else:
            return
        self.trait_set(**{key+'_arr':arr})

    @on_trait_change('solver.solution')
    def _on_soln_changed(self):
        self._set_arr(self.index_name, 'index')
        self._set_arr(self.value_name, 'value')

    @on_trait_change('index_arr,value_arr')
    def _on_arr_changed(self, obj, name, old, new):
        self.pd.set_data(name[:-4], new)

    def _plot_default(self):
        self._set_arr(self.index_name, 'index')
        self._set_arr(self.value_name, 'value')
        plot = Plot(self.pd)
        plot.tools.append(TraitsTool(component=plot))
        plot.tools.append(ZoomTool(component=plot))
        plot.tools.append(PanTool(component=plot))
        plot.x_axis.title = self.index_name
        plot.y_axis.title = self.value_name
        plot.plot(('index', 'value'))
        return plot

    def _index_name_default(self):
        return self.name_list[0]

    def _value_name_default(self):
        return self.name_list[-1]


if __name__ == '__main__':
    from ode import EpidemicODE, LorenzEquation, GenericODE
    import numpy
    ode = EpidemicODE()
    ode = LorenzEquation()
    ode.configure_traits()
    solver = ODESolver(ode=ode, initial_state=[10.,50.,50.], 
                       t=numpy.linspace(0,10,1001))
    plot = ODEPlot(solver=solver)
    plot.configure_traits()

