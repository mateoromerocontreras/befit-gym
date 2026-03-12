import { useMemo, useState } from 'react';
import { Calendar, ChevronDown, ChevronUp, Moon, Dumbbell } from 'lucide-react';
import planService from '../services/planService';

const DAYS = [
    { day: 1, label: 'Lunes' },
    { day: 2, label: 'Martes' },
    { day: 3, label: 'Miércoles' },
    { day: 4, label: 'Jueves' },
    { day: 5, label: 'Viernes' },
    { day: 6, label: 'Sábado' },
    { day: 7, label: 'Domingo' }
];

const WeeklyCalendarView = ({ weeklyPlan = [] }) => {
    const [expandedDay, setExpandedDay] = useState(null);

    const planByDay = useMemo(() => {
        const map = new Map();
        weeklyPlan.forEach((item) => map.set(item.day, item));
        return map;
    }, [weeklyPlan]);

    const toggleDay = (day) => {
        setExpandedDay((prev) => (prev === day ? null : day));
    };

    return (
        <section className="bg-gray-900/40 rounded-2xl border border-gray-800 p-6 mb-8">
            <div className="flex items-center gap-3 mb-6">
                <Calendar className="w-6 h-6 text-accent-lime" />
                <h2 className="text-2xl font-bold text-white">Vista Semanal</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-7 gap-3">
                {DAYS.map(({ day, label }) => {
                    const plan = planByDay.get(day);
                    const hasRoutine = Boolean(plan);
                    const isExpanded = expandedDay === day;

                    return (
                        <div
                            key={day}
                            className={`rounded-xl border p-4 transition-colors ${hasRoutine
                                ? 'bg-gray-900 border-accent-lime/30'
                                : 'bg-gray-950/80 border-gray-800'
                                }`}
                        >
                            <button
                                onClick={() => toggleDay(day)}
                                className="w-full text-left"
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-sm text-gray-400">{label}</p>
                                    {isExpanded ? (
                                        <ChevronUp className="w-4 h-4 text-gray-400" />
                                    ) : (
                                        <ChevronDown className="w-4 h-4 text-gray-400" />
                                    )}
                                </div>

                                {hasRoutine ? (
                                    <>
                                        <p className="text-sm font-semibold text-white line-clamp-2">{plan.day_name}</p>
                                        <p className="text-xs text-accent-lime mt-2">{plan.exercises?.length || 0} ejercicios</p>
                                    </>
                                ) : (
                                    <div className="flex items-center gap-2 text-gray-500 text-sm">
                                        <Moon className="w-4 h-4" />
                                        <span>Rest Day</span>
                                    </div>
                                )}
                            </button>

                            {isExpanded && hasRoutine && (
                                <div className="mt-4 pt-4 border-t border-gray-700 space-y-3">
                                    {(plan.exercises || []).map((exercise) => (
                                        <article key={exercise.id} className="bg-gray-800/70 rounded-lg p-3 border border-gray-700">
                                            <div className="flex items-start justify-between gap-2">
                                                <div>
                                                    <p className="text-sm font-semibold text-white">{exercise.order}. {exercise.name}</p>
                                                    <p className="text-xs text-gray-400 mt-1">
                                                        {planService.getMuscleGroupLabel(exercise.muscle_group)} · {planService.getDifficultyLabel(exercise.difficulty)}
                                                    </p>
                                                </div>
                                                <Dumbbell className="w-4 h-4 text-accent-lime" />
                                            </div>
                                            <div className="flex flex-wrap gap-3 mt-3 text-xs text-gray-300">
                                                <span>{exercise.series} series</span>
                                                <span>{exercise.repetitions} reps</span>
                                            </div>
                                            {exercise.notes && (
                                                <p className="text-xs text-gray-400 mt-2">{exercise.notes}</p>
                                            )}
                                        </article>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </section>
    );
};

export default WeeklyCalendarView;
