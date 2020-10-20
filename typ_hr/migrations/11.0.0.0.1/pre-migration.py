
def clean_vehicle_manager(cr):
    # Delete view with incorrect id the module typ
    cr.execute("""
               UPDATE
                    fleet_vehicle set vehicle_manager=NULL
               WHERE vehicle_manager IS NOT NULL;""")


def migrate(cr, version):
    if not version:
        return
    clean_vehicle_manager(cr)
