import { useI18n } from "@/i18n";

export default function Loading() {
  const { t } = useI18n();
  return <div className="page-container">{t("common.loading")}</div>;
}
