# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class SapImporter(AbstractComponent):
    """ Base importer for SAP """
    _name = "sap.importer"
    _inherit = ['generic.importer.custom', 'base.sap.connector']

    _usage = "direct.record.importer"


class SapBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """
    _name = "sap.batch.importer"
    _inherit = ['base.importer', 'base.sap.connector']

    def run(self, domain=None):
        """ Run the synchronization """
        if domain is None:
            domain = []
        records = self.backend_adapter.search_read(domain)
        for rec in records:
            external_id = self.binder_for().dict2id(rec,in_field=False)
            self._import_record(external_id, external_data=rec)

    def _import_record(self, external_id, external_data=None):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class SapDirectBatchImporter(AbstractComponent):
    """ Import the records directly, without delaying the jobs. """
    _name = "sap.direct.batch.importer"
    _inherit = "sap.batch.importer"

    _usage = "direct.batch.importer"

    def _import_record(self, external_id, external_data=None):
        """ Import the record directly """
        if external_data is None:
            external_data = {}
        self.model.import_record(
            self.backend_record, external_id, external_data=external_data
        )


class SapDelayedBatchImporter(AbstractComponent):
    """ Delay import of the records """
    _name = "sap.delayed.batch.importer"
    _inherit = "sap.batch.importer"

    _usage = "delayed.batch.importer"

    def _import_record(self, external_id, external_data=None, job_options=None):
        """ Delay the import of the records"""
        if external_data is None:
            external_data = {}
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(
            self.backend_record, external_id, external_data=external_data
        )
