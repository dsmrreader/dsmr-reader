from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from dsmr_backend.mixins import ModelUpdateMixin


class EnergySupplierPrice(ModelUpdateMixin, models.Model):
    """
    Represents the price you are charged by your energy supplier. Prices are per unit, which is either one kWh or m3 gas
    """

    start = models.DateField(
        db_index=True,
        verbose_name=_("Contract start"),
    )
    end = models.DateField(
        db_index=True,
        verbose_name=_("Contract end"),
        help_text=_("Set to a far future date when there is not contract end."),
    )
    description = models.CharField(
        max_length=255,
        verbose_name=_("Contract name"),
        help_text=_("For your own reference, i.e. the name of your supplier"),
    )
    electricity_delivered_1_price = models.DecimalField(
        max_digits=11,
        decimal_places=6,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Tariff 1 delivered price (€)"),
        help_text=_(
            "Set to zero when: Unused / Defined in other contract / Not applicable to your situation"
        ),
    )
    electricity_delivered_2_price = models.DecimalField(
        max_digits=11,
        decimal_places=6,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Tariff 2 delivered price (€)"),
        help_text=_(
            "Set to zero when: Unused / Defined in other contract / Not applicable to your situation"
        ),
    )
    gas_price = models.DecimalField(
        max_digits=11,
        decimal_places=6,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Gas price (€)"),
        help_text=_(
            "Set to zero when: Unused / Defined in other contract / Not applicable to your situation"
        ),
    )
    electricity_returned_1_price = models.DecimalField(
        max_digits=11,
        decimal_places=6,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Tariff 1 returned price (€)"),
        help_text=_(
            "Set to zero when: Unused / Defined in other contract / Not applicable to your situation"
        ),
    )
    electricity_returned_2_price = models.DecimalField(
        max_digits=11,
        decimal_places=6,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Tariff 2 returned price (€)"),
        help_text=_(
            "Set to zero when: Unused / Defined in other contract / Not applicable to your situation"
        ),
    )
    fixed_daily_cost = models.DecimalField(
        max_digits=11,
        decimal_places=6,
        default=0,
        verbose_name=_("Fixed daily costs (€)"),
        help_text=_(
            "Both positive and negative prices allowed. Set to zero when: Unused / Defined in other contract / "
            "Not applicable to your situation"
        ),
    )

    def __str__(self):
        return self.description or gettext("Energy supplier price contract")

    class Meta:
        default_permissions = tuple()
        verbose_name = _("Energy supplier (price) contract")
        verbose_name_plural = _("Energy supplier (price) contracts")
