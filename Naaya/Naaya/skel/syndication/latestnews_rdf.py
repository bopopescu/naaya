howmany = -1
if context.numberofitems != 0: howmany = context.numberofitems
return context.getCatalogedObjects(meta_type=context.get_constant('METATYPE_NYNEWS'), approved=1, howmany=howmany, path=['/'.join(x.getPhysicalPath()) for x in context.getMainTopics()])
