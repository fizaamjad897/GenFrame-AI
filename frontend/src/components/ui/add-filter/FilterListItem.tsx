import React from "react";
import { FilterItem } from "./AddFilterPanel";
import PlayerNameFilter from "./PlayerNameFilter";
import ErrorFilter from "./ErrorFilter";
import WarningFilter from "./WarningFilter";
import TagsFilter from "./TagsFilter";
import TagsFromGroupFilter from "./TagsFromGroupFilter";
import GroupsFilter from "./GroupsFilter";
import ConnectivityFilter from "./ConnectivityFilter";
import SyncFilter from "./SyncFilter";
import LastSeenFilter from "./LastSeenFilter";
import ContentChangeAtFilter from "./ContentChangeAtFilter";
import ContentSyncAtFilter from "./ContentSyncAtFilter";
import AppVersionFilter from "./AppVersionFilter";
import OsVersionFilter from "./OsVersionFilter";
import NotesFilter from "./NotesFilter";
import MaintenanceFilter from "./MaintenanceFilter";

interface Props {
  item: FilterItem;
  isOpen: boolean;
  onToggle: () => void;
  onOpenEditor?: () => void;
}

export default function FilterListItem({
  item,
  isOpen,
  onToggle,
  onOpenEditor,
}: Props) {
  const renderEditor = () => {
    switch (item.id) {
      case "player-name":
        return (
            <PlayerNameFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "errors":
        return (
            <ErrorFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "warnings":
        return (
            <WarningFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "tags":
        return (
            <TagsFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "tags-groups":
        return (
            <TagsFromGroupFilter
              onCancel={onToggle}
              onSave={() => onToggle()}
            />
        );
      case "groups":
        return (
            <GroupsFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "connectivity":
        return (
            <ConnectivityFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "last-seen":
        return (
            <LastSeenFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "sync":
        return (
            <SyncFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "content-change-at":
        return (
            <ContentChangeAtFilter
              onCancel={onToggle}
              onSave={() => onToggle()}
            />
        );
      case "content-sync-at":
        return (
            <ContentSyncAtFilter
              onCancel={onToggle}
              onSave={() => onToggle()}
            />
        );
      case "app-versions":
        return (
            <AppVersionFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "os-versions":
        return (
            <OsVersionFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "note":
        return (
            <NotesFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      case "in-maintenance":
        return (
            <MaintenanceFilter onCancel={onToggle} onSave={() => onToggle()} />
        );
      default:
        return (
          <div className="text-sm text-muted-foreground">
            Expanded content for {item.title}
          </div>
        );
    }
  };

  return (
    <div className="py-1">
      <button
        type="button"
        onClick={() => (onOpenEditor ? onOpenEditor() : onToggle())}
        className="w-full flex items-center gap-2 py-2 rounded hover:bg-gray-50"
      >
        <div className="w-4 h-4 flex items-center justify-center text-primary">
          {item.icon}
        </div>
        <div className="text-title font-semibold text-gray-900">
          {item.title}
        </div>
      </button>

      <div
        className={`px-3 transition-all duration-300 ease-in-out overflow-hidden ${
          isOpen ? "max-h-[70vh] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        {isOpen && renderEditor()}
      </div>
    </div>
  );
}
