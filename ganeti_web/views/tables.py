from django_tables2 import Table, Column, LinkColumn, TemplateColumn
from django_tables2.utils import A

from ganeti_web.templatetags.webmgr_tags import (render_storage, render_os,
                                                 abbreviate_fqdn)
from ganeti_web.utilities import hv_prettify


class BaseVMTable(Table):

    status = TemplateColumn(
        template_name="ganeti/virtual_machine/vmfield_status.html",
    )
    hostname = LinkColumn(
        "instance-detail",
        kwargs={"cluster_slug": A("cluster.slug"),
                "instance": A("hostname")},
        verbose_name='name',
    )
    owner = LinkColumn(
        "user-detail-name",
        args=[A("owner")],
    )
    primary_node = Column(verbose_name='node')
    operating_system = Column(verbose_name='OS')
    ram = Column(verbose_name='RAM')
    disk_size = Column(verbose_name='disk space')
    virtual_cpus = Column(verbose_name='vCPUs')

    class Meta:
        sequence = ("status", "hostname", "...")
        order_by = ("hostname")
        empty_text = "No Virtual Machines"

    def __init__(self, *args, **kwargs):
        self.template = "table.html"
        return super(BaseVMTable, self).__init__(*args, **kwargs)

    def render_disk_size(self, value):
        return render_storage(value)

    def render_ram(self, value):
        return render_storage(value)

    def render_operating_system(self, value):
        return render_os(value)

    def render_primary_node(self, value):
        return abbreviate_fqdn(value)


class VMTable(BaseVMTable):

    # This may look weird, but the VirtualMachine View shows clusters, but the
    # cluster view does not, which is why it isn't in the base table.
    cluster = LinkColumn(
        "cluster-detail",
        args=[A("cluster.slug")],
        accessor="cluster.slug",
        verbose_name='cluster'
    )

    class Meta:
        sequence = ("status", "hostname", "cluster", "...")
        order_by = ("hostname")
        empty_text = "No Virtual Machines"


class VMTemplateTable(Table):

    template_name = LinkColumn(
        "template-detail",
        args=[A("cluster.slug"), A("template_name")],
        verbose_name="name"
    )
    description = Column()
    cluster = LinkColumn(
        "cluster-detail",
        args=[A("cluster.slug")],
        accessor="cluster.slug",
        verbose_name="cluster"
    )
    os = Column(verbose_name='OS')
    memory = Column(verbose_name='RAM')
    disk_space = Column()
    vcpus = Column(verbose_name='vCPUs')

    class Meta:
        sequence = ("template_name", "description", "cluster", "os", "memory",
                    "disk_space", "vcpus")
        order_by = ("template_name")
        empty_text = "No Templates"

    def render_os(self, value):
        return render_os(value)

    def render_memory(self, value):
        return render_storage(value)

    def render_disk_space(self, value):
        return render_storage(value)


class ClusterTable(Table):

    cluster = LinkColumn(
        "cluster-detail",
        args=[A("slug")],
        accessor="slug",
        verbose_name='cluster'
    )
    description = Column()
    version = Column(accessor="info.software_version", orderable=False, default="unknown")
    hypervisor = Column(accessor="info.default_hypervisor", orderable=False, default="unknown")
    master_node = LinkColumn(
        "node-detail",
        kwargs={"cluster_slug": A("slug"),
                "host": A("info.master")},
        accessor="info.master",
        orderable=False,
        default="unknown"
    )
    nodes = Column(accessor="nodes.count", orderable=False)
    vms = Column(accessor="virtual_machines.count", verbose_name='VMs',
                 orderable=False)

    class Meta:
        empty_text = "No Clusters"
        sequence = ("cluster", "description", "version", "hypervisor",
                    "master_node", "nodes", "vms")

    def render_hypervisor(self, value):
        return hv_prettify(value)
