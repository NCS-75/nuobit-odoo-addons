# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Template Menu",
    "summary": "This module adds menu entries *Account Chart Templates*, *Account Templates*, "
    "*Account Tax Templates* and *Account Fiscal Pôsition Templates* under "
    "*Accounting > Configuration > Accounting*",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_template_menuitem.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
